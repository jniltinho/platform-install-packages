// Package kaltura is a small typed client for the Kaltura api_v3 used by
// the console: an admin KS cached until shortly before expiry, one retry
// after refreshing the KS on session errors, and streaming uploads.
//
// Every call is a form POST to {service_url}/ with format=1 (JSON) and
// flattened object parameters ("filter:nameLike", "entry:name", …).
package kaltura

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"
)

// APIError is a Kaltura exception returned by api_v3.
type APIError struct {
	Code    string
	Message string
}

func (e *APIError) Error() string { return fmt.Sprintf("kaltura: %s: %s", e.Code, e.Message) }

// ksErrorCodes are the codes that mean "your KS is no longer valid".
var ksErrorCodes = map[string]bool{
	"INVALID_KS": true, "EXPIRED_KS": true, "KS_EXPIRED": true, "INVALID_SESSION_ID": true,
}

// IsKSError reports whether err is a Kaltura session error.
func IsKSError(err error) bool {
	var ae *APIError
	return errors.As(err, &ae) && ksErrorCodes[ae.Code]
}

// Config configures a Client.
type Config struct {
	ServiceURL       string
	UploadServiceURL string
	PartnerID        int
	AdminSecret      string
	UserID           string
	SessionExpiry    time.Duration
	PlaybackHost     string
	HTTPTimeout      time.Duration // per API call (not uploads/streams)
	ConnectTimeout   time.Duration
	UploadTimeout    time.Duration
}

// Client talks to one Kaltura partner.
type Client struct {
	cfg  Config
	http *http.Client
	now  func() time.Time

	mu        sync.Mutex
	ks        string
	ksExpires time.Time
}

// NewClient builds a client. The underlying http.Client has no overall
// timeout so long uploads and media streams are never cut; API calls get
// cfg.HTTPTimeout through their context instead.
func NewClient(cfg Config) *Client {
	if cfg.ConnectTimeout <= 0 {
		cfg.ConnectTimeout = 5 * time.Second
	}
	if cfg.HTTPTimeout <= 0 {
		cfg.HTTPTimeout = 15 * time.Second
	}
	if cfg.UploadTimeout <= 0 {
		cfg.UploadTimeout = 30 * time.Minute
	}
	if cfg.SessionExpiry <= 0 {
		cfg.SessionExpiry = 24 * time.Hour
	}
	if cfg.UserID == "" {
		cfg.UserID = "kaltura-console"
	}
	if cfg.UploadServiceURL == "" {
		cfg.UploadServiceURL = cfg.ServiceURL
	}
	tr := http.DefaultTransport.(*http.Transport).Clone()
	tr.DialContext = (&net.Dialer{Timeout: cfg.ConnectTimeout, KeepAlive: 30 * time.Second}).DialContext
	tr.ResponseHeaderTimeout = cfg.HTTPTimeout
	return &Client{
		cfg: cfg,
		// Redirects are handled by the media proxy itself (allowlist).
		http: &http.Client{Transport: tr, CheckRedirect: func(*http.Request, []*http.Request) error {
			return http.ErrUseLastResponse
		}},
		now: time.Now,
	}
}

// HTTP returns the underlying client (used by the media proxy).
func (c *Client) HTTP() *http.Client { return c.http }

// Config returns the client configuration.
func (c *Client) Config() Config { return c.cfg }

func endpoint(base string) string { return strings.TrimRight(base, "/") + "/" }

// do posts form params to the given api_v3 base and decodes the JSON result into out.
func (c *Client) do(ctx context.Context, base string, params url.Values, out any) error {
	ctx, cancel := context.WithTimeout(ctx, c.cfg.HTTPTimeout)
	defer cancel()
	params.Set("format", "1")
	if params.Get("partnerId") == "" {
		params.Set("partnerId", strconv.Itoa(c.cfg.PartnerID))
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint(base), strings.NewReader(params.Encode()))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")
	resp, err := c.http.Do(req)
	if err != nil {
		return fmt.Errorf("kaltura %s.%s: %w", params.Get("service"), params.Get("action"), err)
	}
	defer resp.Body.Close() //nolint:errcheck // read-only body
	return decode(resp, params, out)
}

func decode(resp *http.Response, params url.Values, out any) error {
	body, err := io.ReadAll(io.LimitReader(resp.Body, 32<<20))
	if err != nil {
		return err
	}
	if resp.StatusCode >= 400 {
		return fmt.Errorf("kaltura %s.%s: HTTP %d", params.Get("service"), params.Get("action"), resp.StatusCode)
	}
	trimmed := bytes.TrimSpace(body)
	if len(trimmed) > 0 && trimmed[0] == '{' {
		var probe struct {
			Code       string `json:"code"`
			Message    string `json:"message"`
			ObjectType string `json:"objectType"`
		}
		if json.Unmarshal(trimmed, &probe) == nil &&
			(strings.Contains(probe.ObjectType, "Exception") || (probe.ObjectType == "" && probe.Code != "" && probe.Message != "")) {
			return &APIError{Code: probe.Code, Message: probe.Message}
		}
	}
	if out == nil {
		return nil
	}
	if err := json.Unmarshal(trimmed, out); err != nil {
		return fmt.Errorf("kaltura %s.%s: decoding response: %w", params.Get("service"), params.Get("action"), err)
	}
	return nil
}

// adminKS returns a cached admin KS, starting a new session when needed.
func (c *Client) adminKS(ctx context.Context, force bool) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if !force && c.ks != "" && c.now().Before(c.ksExpires) {
		return c.ks, nil
	}
	var ks string
	params := url.Values{
		"service": {"session"}, "action": {"start"},
		"secret": {c.cfg.AdminSecret}, "userId": {c.cfg.UserID},
		"type": {"2"}, "expiry": {strconv.Itoa(int(c.cfg.SessionExpiry.Seconds()))},
	}
	if err := c.do(ctx, c.cfg.ServiceURL, params, &ks); err != nil {
		return "", err
	}
	if ks == "" {
		return "", errors.New("kaltura: session.start returned an empty KS")
	}
	ttl := c.cfg.SessionExpiry - 5*time.Minute
	if ttl < time.Minute {
		ttl = time.Minute
	}
	c.ks, c.ksExpires = ks, c.now().Add(ttl)
	return ks, nil
}

// ForgetKS drops the cached KS.
func (c *Client) ForgetKS() {
	c.mu.Lock()
	c.ks = ""
	c.mu.Unlock()
}

// withKS runs fn with the admin KS and retries once with a fresh KS on a session error.
func (c *Client) withKS(ctx context.Context, fn func(ks string) error) error {
	ks, err := c.adminKS(ctx, false)
	if err != nil {
		return err
	}
	err = fn(ks)
	if !IsKSError(err) {
		return err
	}
	ks, err = c.adminKS(ctx, true)
	if err != nil {
		return err
	}
	return fn(ks)
}

// Call performs an authenticated api_v3 call.
func (c *Client) Call(ctx context.Context, service, action string, params url.Values, out any) error {
	return c.withKS(ctx, func(ks string) error {
		p := url.Values{}
		for k, v := range params {
			p[k] = append([]string(nil), v...)
		}
		p.Set("service", service)
		p.Set("action", action)
		p.Set("ks", ks)
		return c.do(ctx, c.cfg.ServiceURL, p, out)
	})
}

// Ping calls system.ping (no KS).
func (c *Client) Ping(ctx context.Context) error {
	var ok bool
	if err := c.do(ctx, c.cfg.ServiceURL, url.Values{"service": {"system"}, "action": {"ping"}}, &ok); err != nil {
		return err
	}
	if !ok {
		return errors.New("kaltura: system.ping returned false")
	}
	return nil
}

// CheckSession forces a fresh admin KS (used by the health page).
func (c *Client) CheckSession(ctx context.Context) error {
	_, err := c.adminKS(ctx, true)
	return err
}
