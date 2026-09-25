package kaltura

import (
	"context"
	"fmt"
	"net/url"
	"regexp"
	"strconv"
	"strings"
)

// entryIDPattern matches Kaltura entry IDs such as 0_8irzw99z.
var entryIDPattern = regexp.MustCompile(`^[0-9]_[a-z0-9]{8}$`)

// ValidEntryID reports whether id looks like a Kaltura entry ID.
func ValidEntryID(id string) bool { return entryIDPattern.MatchString(id) }

// Entry is the subset of KalturaMediaEntry used by the console.
type Entry struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Description  string `json:"description"`
	Status       int    `json:"status"`
	Duration     int    `json:"duration"`
	CreatedAt    int64  `json:"createdAt"`
	UpdatedAt    int64  `json:"updatedAt"`
	Plays        int    `json:"plays"`
	Width        int    `json:"width"`
	Height       int    `json:"height"`
	PartnerID    int    `json:"partnerId"`
	ThumbnailURL string `json:"thumbnailUrl,omitempty"`
}

// EntryList is a page of entries.
type EntryList struct {
	Objects    []Entry `json:"objects"`
	TotalCount int     `json:"totalCount"`
}

// Flavor is the subset of KalturaFlavorAsset used by the console.
type Flavor struct {
	ID             string `json:"id"`
	EntryID        string `json:"entryId"`
	FlavorParamsID int    `json:"flavorParamsId"`
	Status         int    `json:"status"`
	IsOriginal     bool   `json:"isOriginal"`
	FileExt        string `json:"fileExt"`
	Width          int    `json:"width"`
	Height         int    `json:"height"`
	Size           int64  `json:"size"` // KB
	Bitrate        int    `json:"bitrate"`
	VideoCodecID   string `json:"videoCodecId"`
}

// ListOptions filters media.list.
type ListOptions struct {
	NameLike string
	StatusIn []int
	Page     int
	PageSize int
}

// ListMedia calls media.list, newest first.
func (c *Client) ListMedia(ctx context.Context, o ListOptions) (*EntryList, error) {
	if o.Page < 1 {
		o.Page = 1
	}
	if o.PageSize < 1 {
		o.PageSize = 20
	}
	if o.PageSize > 500 {
		o.PageSize = 500
	}
	p := url.Values{
		"filter:objectType": {"KalturaMediaEntryFilter"},
		"filter:orderBy":    {"-createdAt"},
		"pager:objectType":  {"KalturaFilterPager"},
		"pager:pageIndex":   {strconv.Itoa(o.Page)},
		"pager:pageSize":    {strconv.Itoa(o.PageSize)},
	}
	if s := strings.TrimSpace(o.NameLike); s != "" {
		p.Set("filter:nameLike", s)
	}
	if len(o.StatusIn) > 0 {
		parts := make([]string, len(o.StatusIn))
		for i, s := range o.StatusIn {
			parts[i] = strconv.Itoa(s)
		}
		p.Set("filter:statusIn", strings.Join(parts, ","))
	}
	var out EntryList
	if err := c.Call(ctx, "media", "list", p, &out); err != nil {
		return nil, err
	}
	if out.Objects == nil {
		out.Objects = []Entry{}
	}
	return &out, nil
}

// CountByStatuses returns how many entries have one of the statuses.
func (c *Client) CountByStatuses(ctx context.Context, statuses []int) (int, error) {
	l, err := c.ListMedia(ctx, ListOptions{StatusIn: statuses, PageSize: 1})
	if err != nil {
		return 0, err
	}
	return l.TotalCount, nil
}

// GetMedia calls media.get.
func (c *Client) GetMedia(ctx context.Context, entryID string) (*Entry, error) {
	var e Entry
	if err := c.Call(ctx, "media", "get", url.Values{"entryId": {entryID}}, &e); err != nil {
		return nil, err
	}
	if e.ID != entryID || e.PartnerID != c.cfg.PartnerID {
		return nil, &APIError{Code: "ENTRY_ID_NOT_FOUND", Message: "entry does not belong to configured partner"}
	}
	return &e, nil
}

// AddMedia calls media.add for a video entry.
func (c *Client) AddMedia(ctx context.Context, name, description string) (*Entry, error) {
	var e Entry
	p := url.Values{
		"entry:objectType": {"KalturaMediaEntry"},
		"entry:mediaType":  {"1"},
		"entry:name":       {name},
	}
	if description != "" {
		p.Set("entry:description", description)
	}
	if err := c.Call(ctx, "media", "add", p, &e); err != nil {
		return nil, err
	}
	return &e, nil
}

// UpdateMedia calls media.update for name and description.
func (c *Client) UpdateMedia(ctx context.Context, entryID, name, description string) (*Entry, error) {
	var e Entry
	p := url.Values{
		"entryId":                {entryID},
		"mediaEntry:objectType":  {"KalturaMediaEntry"},
		"mediaEntry:name":        {name},
		"mediaEntry:description": {description},
	}
	if err := c.Call(ctx, "media", "update", p, &e); err != nil {
		return nil, err
	}
	return &e, nil
}

// DeleteMedia calls media.delete.
func (c *Client) DeleteMedia(ctx context.Context, entryID string) error {
	return c.Call(ctx, "media", "delete", url.Values{"entryId": {entryID}}, nil)
}

// ListFlavors calls flavorAsset.list for an entry.
func (c *Client) ListFlavors(ctx context.Context, entryID string) ([]Flavor, error) {
	var out struct {
		Objects []Flavor `json:"objects"`
	}
	p := url.Values{"filter:objectType": {"KalturaAssetFilter"}, "filter:entryIdEqual": {entryID}}
	if err := c.Call(ctx, "flavorAsset", "list", p, &out); err != nil {
		return nil, err
	}
	if out.Objects == nil {
		out.Objects = []Flavor{}
	}
	return out.Objects, nil
}

func (c *Client) deliveryBase(entryID string) string {
	pid := c.cfg.PartnerID
	return fmt.Sprintf("%s/p/%d/sp/%d00", strings.TrimRight(c.cfg.PlaybackHost, "/"), pid, pid)
}

// PlaybackURL is the progressive MP4 playManifest URL of an entry.
func (c *Client) PlaybackURL(entryID, flavorID string) string {
	protocol := "http"
	if strings.HasPrefix(strings.ToLower(c.cfg.PlaybackHost), "https://") {
		protocol = "https"
	}
	return c.deliveryBase(entryID) + "/playManifest/entryId/" + entryID +
		"/format/url/protocol/" + protocol + "/flavorIds/" + flavorID + "/a.mp4"
}

// ThumbnailURL is the thumbnail URL of an entry.
func (c *Client) ThumbnailURL(entryID string) string {
	return c.deliveryBase(entryID) + "/thumbnail/entry_id/" + entryID + "/width/640"
}

// BestPlaybackFlavor selects a ready, entry-owned MP4/H.264 asset. Originals
// win at equal resolution to avoid another compression generation/frame-rate loss.
func BestPlaybackFlavor(entryID string, flavors []Flavor) (Flavor, bool) {
	var best Flavor
	found := false
	for _, f := range flavors {
		codec := strings.ToLower(f.VideoCodecID)
		if f.EntryID != entryID || !ValidEntryID(f.ID) || f.Status != 2 ||
			!strings.EqualFold(f.FileExt, "mp4") || (codec != "avc1" && codec != "h264") ||
			f.Width <= 0 || f.Height <= 0 {
			continue
		}
		if !found || betterPlaybackFlavor(f, best) {
			best, found = f, true
		}
	}
	return best, found
}

func betterPlaybackFlavor(a, b Flavor) bool {
	// Floating-point area avoids integer overflow from malformed upstream dimensions.
	areaA, areaB := float64(a.Width)*float64(a.Height), float64(b.Width)*float64(b.Height)
	if areaA != areaB {
		return areaA > areaB
	}
	if a.IsOriginal != b.IsOriginal {
		return a.IsOriginal
	}
	if a.Bitrate != b.Bitrate {
		return a.Bitrate > b.Bitrate
	}
	return a.ID < b.ID
}
