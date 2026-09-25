package kaltura

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/goleak"
)

func TestMain(m *testing.M) { goleak.VerifyTestMain(m) }

// fakeAPI is a minimal api_v3 double.
type fakeAPI struct {
	mu             sync.Mutex
	sessions       int32
	validKS        string
	expireNextCall atomic.Bool // next authenticated call answers EXPIRED_KS once
	failAction     string      // "service.action" that answers an exception
	uploadBytes    []int
	deleted        []string
	uploadEarly    bool // answer uploadToken.upload before reading the body
}

func (f *fakeAPI) handler(t *testing.T) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		isMultipart := strings.HasPrefix(r.Header.Get("Content-Type"), "multipart/")
		if isMultipart && f.uploadEarly {
			w.Header().Set("Content-Type", "application/json")
			_, _ = io.WriteString(w, `{"code":"UPLOAD_ERROR","message":"early","objectType":"KalturaAPIException"}`)
			return
		}
		var service, action, ks string
		var fileLen int
		if isMultipart {
			mr, err := r.MultipartReader()
			require.NoError(t, err)
			for {
				p, err := mr.NextPart()
				if err == io.EOF {
					break
				}
				require.NoError(t, err)
				b, _ := io.ReadAll(p)
				switch p.FormName() {
				case "service":
					service = string(b)
				case "action":
					action = string(b)
				case "ks":
					ks = string(b)
				case "fileData":
					fileLen = len(b)
				}
			}
		} else {
			require.NoError(t, r.ParseForm())
			service, action, ks = r.PostForm.Get("service"), r.PostForm.Get("action"), r.PostForm.Get("ks")
			assert.Equal(t, "1", r.PostForm.Get("format"))
		}
		w.Header().Set("Content-Type", "application/json")
		exc := func(code string) {
			if _, err := fmt.Fprintf(w, `{"code":%q,"message":"x","objectType":"KalturaAPIException","args":{}}`, code); err != nil {
				t.Errorf("writing fake response: %v", err)
			}
		}
		if service == "system" && action == "ping" {
			_, _ = io.WriteString(w, "true")
			return
		}
		if service == "session" && action == "start" {
			n := atomic.AddInt32(&f.sessions, 1)
			f.mu.Lock()
			f.validKS = fmt.Sprintf("KS%d", n)
			f.mu.Unlock()
			if _, err := fmt.Fprintf(w, "%q", f.validKS); err != nil {
				t.Errorf("writing fake response: %v", err)
			}
			return
		}
		f.mu.Lock()
		valid := ks == f.validKS
		f.mu.Unlock()
		if !valid || f.expireNextCall.CompareAndSwap(true, false) {
			exc("EXPIRED_KS")
			return
		}
		if f.failAction == service+"."+action {
			exc("SOME_ERROR")
			return
		}
		switch service + "." + action {
		case "media.list":
			_, _ = io.WriteString(w, `{"objects":[{"id":"0_aaaaaaaa","name":"A","status":2,"duration":61,"createdAt":1}],"totalCount":7,"objectType":"KalturaMediaListResponse"}`)
		case "media.add":
			_, _ = io.WriteString(w, `{"id":"0_bbbbbbbb","name":"B","status":7,"objectType":"KalturaMediaEntry"}`)
		case "media.addContent":
			_, _ = io.WriteString(w, `{"id":"0_bbbbbbbb","name":"B","status":1,"objectType":"KalturaMediaEntry"}`)
		case "media.delete":
			f.mu.Lock()
			f.deleted = append(f.deleted, r.PostForm.Get("entryId"))
			f.mu.Unlock()
			_, _ = io.WriteString(w, "null")
		case "uploadToken.add":
			_, _ = io.WriteString(w, `{"id":"0_tok","status":0,"objectType":"KalturaUploadToken"}`)
		case "uploadToken.upload":
			f.mu.Lock()
			f.uploadBytes = append(f.uploadBytes, fileLen)
			f.mu.Unlock()
			_, _ = io.WriteString(w, `{"id":"0_tok","status":2,"objectType":"KalturaUploadToken"}`)
		case "flavorAsset.list":
			_, _ = io.WriteString(w, `{"objects":[{"id":"0_f","flavorParamsId":0,"status":2,"isOriginal":true,"width":640,"height":360,"size":151,"bitrate":123}],"totalCount":1}`)
		default:
			exc("SERVICE_FORBIDDEN")
		}
	}
}

func newTestClient(t *testing.T, f *fakeAPI) *Client {
	t.Helper()
	srv := httptest.NewServer(f.handler(t))
	t.Cleanup(srv.Close)
	return NewClient(Config{ServiceURL: srv.URL + "/api_v3", PartnerID: 102, AdminSecret: "s", PlaybackHost: srv.URL})
}

func TestKSCachedAndRetriedOnce(t *testing.T) {
	f := &fakeAPI{}
	c := newTestClient(t, f)
	ctx := context.Background()

	l, err := c.ListMedia(ctx, ListOptions{NameLike: "A"})
	require.NoError(t, err)
	assert.Equal(t, 7, l.TotalCount)
	_, err = c.ListMedia(ctx, ListOptions{})
	require.NoError(t, err)
	assert.EqualValues(t, 1, atomic.LoadInt32(&f.sessions), "KS is cached")

	f.expireNextCall.Store(true)
	_, err = c.ListMedia(ctx, ListOptions{})
	require.NoError(t, err, "EXPIRED_KS triggers one refresh and retry")
	assert.EqualValues(t, 2, atomic.LoadInt32(&f.sessions))
}

func TestAPIErrorMapping(t *testing.T) {
	f := &fakeAPI{failAction: "media.list"}
	c := newTestClient(t, f)
	_, err := c.ListMedia(context.Background(), ListOptions{})
	var ae *APIError
	require.ErrorAs(t, err, &ae)
	assert.Equal(t, "SOME_ERROR", ae.Code)
	assert.False(t, IsKSError(err))
	assert.True(t, IsKSError(&APIError{Code: "INVALID_SESSION_ID"}))
	require.NoError(t, c.Ping(context.Background()))
}

func stagedFile(t *testing.T, size int) string {
	t.Helper()
	p := filepath.Join(t.TempDir(), "v.mp4")
	require.NoError(t, os.WriteFile(p, []byte(strings.Repeat("x", size)), 0o600))
	return p
}

func TestUploadRetryRebuildsBody(t *testing.T) {
	f := &fakeAPI{}
	path := stagedFile(t, 300_000)
	// Make uploadToken.upload fail with EXPIRED_KS once: the first attempt
	// consumes the body, the retry must send the whole file again.
	calls := 0
	orig := f.handler(t)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasPrefix(r.Header.Get("Content-Type"), "multipart/") && calls == 0 {
			calls++
			_, _ = io.Copy(io.Discard, r.Body)
			_, _ = io.WriteString(w, `{"code":"EXPIRED_KS","message":"x","objectType":"KalturaAPIException"}`)
			return
		}
		orig(w, r)
	}))
	defer srv.Close()
	c := NewClient(Config{ServiceURL: srv.URL, PartnerID: 102, AdminSecret: "s"})

	var last int64
	e, err := c.UploadFile(context.Background(), path, "v.mp4", "B", "", func(n int64) { last = n })
	require.NoError(t, err)
	assert.Equal(t, "0_bbbbbbbb", e.ID)
	assert.Equal(t, []int{300_000}, f.uploadBytes, "retry sent the full file")
	assert.EqualValues(t, 300_000, last)
}

func TestUploadEarlyResponseNoLeakAndCleanup(t *testing.T) {
	f := &fakeAPI{uploadEarly: true}
	c := newTestClient(t, f)
	_, err := c.UploadFile(context.Background(), stagedFile(t, 5<<20), "v.mp4", "B", "", nil)
	var ue *UploadError
	require.ErrorAs(t, err, &ue)
	assert.Equal(t, StepUpload, ue.Step)
	assert.Equal(t, []string{"0_bbbbbbbb"}, f.deleted, "orphan entry deleted")
}

func TestUploadAttachFailureCleansUp(t *testing.T) {
	f := &fakeAPI{failAction: "media.addContent"}
	c := newTestClient(t, f)
	_, err := c.UploadFile(context.Background(), stagedFile(t, 10), "v.mp4", "B", "", nil)
	var ue *UploadError
	require.ErrorAs(t, err, &ue)
	assert.Equal(t, StepAttach, ue.Step)
	assert.Equal(t, []string{"0_bbbbbbbb"}, f.deleted)
}

func TestHelpers(t *testing.T) {
	c := NewClient(Config{ServiceURL: "http://k/api_v3", PartnerID: 102, PlaybackHost: "http://k/"})
	assert.Equal(t, "http://k/p/102/sp/10200/playManifest/entryId/0_abcdefgh/format/url/protocol/http/a.mp4", c.PlaybackURL("0_abcdefgh"))
	assert.True(t, ValidEntryID("0_8irzw99z"))
	assert.False(t, ValidEntryID("../etc/passwd"))
	assert.Equal(t, GroupProcessing, EntryStatusGroup(4))
	assert.Equal(t, GroupError, EntryStatusGroup(-2))
	assert.Equal(t, GroupOther, EntryStatusGroup(7))
	assert.Equal(t, "Não aplicável", FlavorStatusLabel(4))
}
