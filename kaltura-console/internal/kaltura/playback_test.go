package kaltura

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestBestPlaybackFlavor(t *testing.T) {
	base := Flavor{
		ID: "0_aaaaaaaa", EntryID: "0_abcdefgh", Status: 2, FileExt: "mp4",
		VideoCodecID: "avc1", Width: 1920, Height: 1080, Bitrate: 5000,
	}
	changed := func(fn func(*Flavor)) Flavor { f := base; fn(&f); return f }
	low := changed(func(f *Flavor) { f.ID = "0_bbbbbbbb"; f.Width = 640; f.Height = 360 })
	original := changed(func(f *Flavor) { f.ID = "0_cccccccc"; f.IsOriginal = true; f.Bitrate = 4000 })
	high := changed(func(f *Flavor) { f.ID = "0_dddddddd"; f.Bitrate = 6000 })
	for _, tt := range []struct {
		name    string
		flavors []Flavor
		want    string
	}{
		{"resolution", []Flavor{low, base}, base.ID},
		{"original retains quality", []Flavor{high, original}, original.ID},
		{"bitrate", []Flavor{base, high}, high.ID},
		{"tie ID", []Flavor{changed(func(f *Flavor) { f.ID = "0_zzzzzzzz" }), base}, base.ID},
		{"wrong entry", []Flavor{changed(func(f *Flavor) { f.EntryID = "0_otherone" })}, ""},
		{"invalid ID", []Flavor{changed(func(f *Flavor) { f.ID = "../bad" })}, ""},
		{"not ready", []Flavor{changed(func(f *Flavor) { f.Status = 1 })}, ""},
		{"wrong container", []Flavor{changed(func(f *Flavor) { f.FileExt = "webm" })}, ""},
		{"unsupported codec", []Flavor{changed(func(f *Flavor) { f.VideoCodecID = "hevc" })}, ""},
		{"missing dimensions", []Flavor{changed(func(f *Flavor) { f.Width = 0 })}, ""},
		{"case and codec alias", []Flavor{changed(func(f *Flavor) { f.FileExt = "MP4"; f.VideoCodecID = "H264" })}, base.ID},
		{"empty", nil, ""},
	} {
		t.Run(tt.name, func(t *testing.T) {
			got, ok := BestPlaybackFlavor(base.EntryID, tt.flavors)
			require.Equal(t, tt.want != "", ok)
			require.Equal(t, tt.want, got.ID)
		})
	}
}
