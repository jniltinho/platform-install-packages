package server

import (
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"errors"
	"io"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

type uploadAPI struct {
	mu            sync.Mutex
	fail          string
	calls         []string
	uploaded      []byte
	deleted       chan struct{}
	attachStarted chan struct{}
	release       chan struct{}
}

func (a *uploadAPI) handler(t *testing.T) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var service, action string
		var data []byte
		if strings.HasPrefix(r.Header.Get("Content-Type"), "multipart/") {
			reader, err := r.MultipartReader()
			if err != nil {
				t.Error(err)
				return
			}
			for {
				p, err := reader.NextPart()
				if errors.Is(err, io.EOF) {
					break
				}
				if err != nil {
					t.Error(err)
					return
				}
				value, err := io.ReadAll(p)
				if err != nil {
					t.Error(err)
					return
				}
				switch p.FormName() {
				case "service":
					service = string(value)
				case "action":
					action = string(value)
				case "fileData":
					data = value
				}
			}
		} else {
			if err := r.ParseForm(); err != nil {
				t.Error(err)
				return
			}
			service, action = r.Form.Get("service"), r.Form.Get("action")
		}
		step := service + "." + action
		a.mu.Lock()
		a.calls = append(a.calls, step)
		if data != nil {
			a.uploaded = data
		}
		a.mu.Unlock()
		if step == "media.addContent" && a.attachStarted != nil {
			close(a.attachStarted)
			select {
			case <-r.Context().Done():
				return
			case <-a.release:
				return
			}
		}
		var reply any
		switch step {
		case a.fail:
			reply = map[string]string{"objectType": "KalturaAPIException", "code": "TEST_FAILURE", "message": "failed"}
		case "session.start":
			reply = "test-ks"
		case "media.delete":
			if a.deleted != nil {
				close(a.deleted)
			}
			reply = nil
		case "uploadToken.add":
			reply = map[string]string{"id": "0_token"}
		case "uploadToken.upload":
			reply = map[string]string{"id": "0_token"}
		default:
			reply = map[string]any{"id": "0_abcdefgh", "partnerId": 102, "name": "Test", "status": 1}
		}
		if err := json.NewEncoder(w).Encode(reply); err != nil {
			t.Error(err)
		}
	}
}

func uploadFixture(t *testing.T, api *uploadAPI) (*httptest.Server, harness, <-chan struct{}) {
	t.Helper()
	upstream := httptest.NewServer(api.handler(t))
	t.Cleanup(upstream.Close)
	h := setup(t, upstream.URL, "admin")
	finished := make(chan struct{}, 1)
	front := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() { finished <- struct{}{} }()
		h.e.ServeHTTP(w, r)
	}))
	t.Cleanup(front.Close)
	return front, h, finished
}

func bmffData() []byte {
	data := make([]byte, 1024)
	binary.BigEndian.PutUint32(data[:4], 16)
	copy(data[4:8], "ftyp")
	copy(data[8:12], "isom")
	return data
}

func uploadRequest(t *testing.T, ctx context.Context, front *httptest.Server, h harness) *http.Request {
	t.Helper()
	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	require.NoError(t, writer.WriteField("name", "Test"))
	file, err := writer.CreateFormFile("file", "test.mp4")
	require.NoError(t, err)
	_, err = file.Write(bmffData())
	require.NoError(t, err)
	require.NoError(t, writer.Close())
	req, err := http.NewRequestWithContext(ctx, "POST", front.URL+"/api/media", &body)
	require.NoError(t, err)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set(csrfHeader, h.csrf)
	req.AddCookie(h.cookie)
	return req
}

func waitUploadCleanup(t *testing.T, h harness, finished <-chan struct{}) {
	t.Helper()
	select {
	case <-finished:
	case <-time.After(5 * time.Second):
		t.Fatal("upload handler did not finish")
	}
	files, err := os.ReadDir(h.s.cfg.Upload.TmpDir)
	require.NoError(t, err)
	require.Empty(t, files)
	require.Empty(t, h.s.uploads, "upload slot must be released")
}

func TestUploadSuccessAndStepFailures(t *testing.T) {
	for _, step := range []string{"", "media.add", "uploadToken.add", "uploadToken.upload", "media.addContent"} {
		name := step
		if name == "" {
			name = "success"
		}
		t.Run(name, func(t *testing.T) {
			api := &uploadAPI{fail: step}
			front, h, finished := uploadFixture(t, api)
			resp, err := front.Client().Do(uploadRequest(t, context.Background(), front, h))
			require.NoError(t, err)
			defer func() { require.NoError(t, resp.Body.Close()) }()
			body, err := io.ReadAll(resp.Body)
			require.NoError(t, err)
			waitUploadCleanup(t, h, finished)
			api.mu.Lock()
			defer api.mu.Unlock()
			if step == "" {
				require.Equal(t, http.StatusCreated, resp.StatusCode, string(body))
				require.Contains(t, string(body), "0_abcdefgh")
				require.Equal(t, bmffData(), api.uploaded)
				require.NotContains(t, api.calls, "media.delete")
				require.Equal(t, []string{"session.start", "media.add", "uploadToken.add", "uploadToken.upload", "media.addContent"}, api.calls)
			} else {
				require.Equal(t, http.StatusBadGateway, resp.StatusCode, string(body))
				if step == "media.add" {
					require.NotContains(t, api.calls, "media.delete")
				} else {
					require.Equal(t, "media.delete", api.calls[len(api.calls)-1], "created orphan must be deleted")
				}
			}
		})
	}
}

func TestUploadCancellationDeletesOrphan(t *testing.T) {
	api := &uploadAPI{attachStarted: make(chan struct{}), deleted: make(chan struct{}), release: make(chan struct{})}
	defer close(api.release)
	front, h, finished := uploadFixture(t, api)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	req := uploadRequest(t, ctx, front, h)
	result := make(chan error, 1)
	go func() {
		resp, err := front.Client().Do(req)
		if resp != nil {
			err = errors.Join(err, resp.Body.Close())
		}
		result <- err
	}()
	select {
	case <-api.attachStarted:
	case <-time.After(5 * time.Second):
		t.Fatal("attach was not reached")
	}
	cancel()
	require.Error(t, <-result)
	select {
	case <-api.deleted:
	case <-time.After(5 * time.Second):
		t.Fatal("orphan cleanup did not run after browser cancellation")
	}
	waitUploadCleanup(t, h, finished)
}

func TestUploadBrowserDisconnectDuringStaging(t *testing.T) {
	api := &uploadAPI{}
	front, h, finished := uploadFixture(t, api)
	reader, writer := io.Pipe()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	defer func() { require.NoError(t, reader.Close()) }()
	defer func() { require.NoError(t, writer.Close()) }()
	req, err := http.NewRequestWithContext(ctx, "POST", front.URL+"/api/media", reader)
	require.NoError(t, err)
	req.Header.Set("Content-Type", "multipart/form-data; boundary=staging")
	req.Header.Set(csrfHeader, h.csrf)
	req.AddCookie(h.cookie)
	result := make(chan error, 1)
	go func() {
		resp, err := front.Client().Do(req)
		if resp != nil {
			err = errors.Join(err, resp.Body.Close())
		}
		result <- err
	}()
	prefix := "--staging\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\nTest\r\n" +
		"--staging\r\nContent-Disposition: form-data; name=\"file\"; filename=\"test.mp4\"\r\n" +
		"Content-Type: video/mp4\r\n\r\n"
	_, err = io.WriteString(writer, prefix+strings.Repeat("x", 8192))
	require.NoError(t, err)
	require.Eventually(t, func() bool {
		files, err := os.ReadDir(h.s.cfg.Upload.TmpDir)
		return err == nil && len(files) == 1
	}, 5*time.Second, 10*time.Millisecond)
	cancel()
	require.NoError(t, writer.CloseWithError(context.Canceled))
	require.Error(t, <-result)
	waitUploadCleanup(t, h, finished)
	api.mu.Lock()
	defer api.mu.Unlock()
	require.Empty(t, api.calls, "incomplete staging must not contact Kaltura")
}
