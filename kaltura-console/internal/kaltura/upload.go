package kaltura

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"math"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
)

// Upload steps, reported in UploadError so the UI can say what failed.
const (
	StepAdd    = "add"    // media.add
	StepToken  = "token"  // uploadToken.add
	StepUpload = "upload" // uploadToken.upload
	StepAttach = "attach" // media.addContent
)

// UploadError wraps the failure of one upload step.
type UploadError struct {
	Step    string
	EntryID string
	Err     error
}

func (e *UploadError) Error() string { return fmt.Sprintf("upload step %s: %v", e.Step, e.Err) }
func (e *UploadError) Unwrap() error { return e.Err }

// UploadFile creates a media entry and attaches the staged file at path:
// media.add → uploadToken.add → uploadToken.upload → media.addContent.
// If a step fails after the entry was created, the entry is deleted (best
// effort) so no orphan remains. progress, when not nil, is called with the
// number of bytes sent to Kaltura so far.
func (c *Client) UploadFile(ctx context.Context, path, fileName, name, description string, progress func(int64)) (*Entry, error) {
	ctx, cancel := context.WithTimeout(ctx, c.cfg.UploadTimeout)
	defer cancel()

	entry, err := c.AddMedia(ctx, name, description)
	if err != nil {
		return nil, &UploadError{Step: StepAdd, Err: err}
	}
	cleanup := func(step string, err error) (*Entry, error) {
		// Use a fresh context: ctx may be the reason we failed.
		delCtx, delCancel := context.WithTimeout(context.Background(), c.cfg.HTTPTimeout)
		defer delCancel()
		_ = c.DeleteMedia(delCtx, entry.ID)
		return nil, &UploadError{Step: step, EntryID: entry.ID, Err: err}
	}

	var tok struct {
		ID string `json:"id"`
	}
	if err := c.Call(ctx, "uploadToken", "add", url.Values{"uploadToken:objectType": {"KalturaUploadToken"}}, &tok); err != nil {
		return cleanup(StepToken, err)
	}
	if tok.ID == "" {
		return cleanup(StepToken, errors.New("empty upload token id"))
	}

	err = c.withKS(ctx, func(ks string) error {
		return c.uploadOnce(ctx, ks, tok.ID, path, fileName, progress)
	})
	if err != nil {
		return cleanup(StepUpload, err)
	}

	var attached Entry
	p := url.Values{
		"entryId":             {entry.ID},
		"resource:objectType": {"KalturaUploadedFileTokenResource"},
		"resource:token":      {tok.ID},
	}
	if err := c.Call(ctx, "media", "addContent", p, &attached); err != nil {
		return cleanup(StepAttach, err)
	}
	return &attached, nil
}

// uploadOnce streams one multipart uploadToken.upload request. The body is
// rebuilt from the file on every call, so a KS retry never reuses a
// consumed stream. The writer goroutine is always joined before returning.
func (c *Client) uploadOnce(ctx context.Context, ks, token, path, fileName string, progress func(int64)) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close() //nolint:errcheck // read-only

	info, err := f.Stat()
	if err != nil {
		return err
	}
	if !info.Mode().IsRegular() {
		return errors.New("upload source must be a regular file")
	}
	fields := map[string]string{
		"service": "uploadToken", "action": "upload", "format": "1",
		"partnerId": strconv.Itoa(c.cfg.PartnerID), "ks": ks, "uploadTokenId": token,
	}
	pr, pw := io.Pipe()
	mw := multipart.NewWriter(pw)
	// PHP-FPM may silently discard chunked multipart bodies. Measure only framing,
	// then stream the file with an exact Content-Length (no file-sized buffer).
	var framing bytes.Buffer
	measure := multipart.NewWriter(&framing)
	if err := measure.SetBoundary(mw.Boundary()); err != nil {
		return err
	}
	if err := writeUploadBody(measure, bytes.NewReader(nil), fileName, fields, nil); err != nil {
		return err
	}
	if err := measure.Close(); err != nil {
		return err
	}
	if info.Size() > math.MaxInt64-int64(framing.Len()) {
		return errors.New("upload size exceeds HTTP content length")
	}
	contentLength := info.Size() + int64(framing.Len())
	done := make(chan error, 1)
	go func() {
		err := writeUploadBody(mw, f, fileName, fields, progress)
		if err == nil {
			err = mw.Close()
		}
		pw.CloseWithError(err) //nolint:errcheck // always returns nil
		done <- err
	}()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint(c.cfg.UploadServiceURL), pr)
	if err != nil {
		pr.CloseWithError(err) //nolint:errcheck
		<-done
		return err
	}
	req.Header.Set("Content-Type", mw.FormDataContentType())
	req.ContentLength = contentLength
	resp, err := c.http.Do(req)
	// Whatever happened, stop the writer (a no-op if it already finished)
	// and wait for it, so an early upstream response never leaks it.
	pr.CloseWithError(errors.New("upload request finished")) //nolint:errcheck
	writeErr := <-done
	if err != nil {
		return err
	}
	defer resp.Body.Close() //nolint:errcheck
	if derr := decode(resp, url.Values{"service": {"uploadToken"}, "action": {"upload"}}, nil); derr != nil {
		return derr
	}
	if writeErr != nil {
		return fmt.Errorf("upload body: %w", writeErr)
	}
	return nil
}

func writeUploadBody(mw *multipart.Writer, f io.Reader, fileName string, fields map[string]string, progress func(int64)) error {
	for k, v := range fields {
		if err := mw.WriteField(k, v); err != nil {
			return err
		}
	}
	part, err := mw.CreateFormFile("fileData", filepath.Base(fileName))
	if err != nil {
		return err
	}
	var src = f
	if progress != nil {
		src = &progressReader{r: f, fn: progress}
	}
	_, err = io.Copy(part, src)
	return err
}

type progressReader struct {
	r  io.Reader
	n  int64
	fn func(int64)
}

func (p *progressReader) Read(b []byte) (int, error) {
	n, err := p.r.Read(b)
	p.n += int64(n)
	p.fn(p.n)
	return n, err
}
