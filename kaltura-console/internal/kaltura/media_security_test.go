package kaltura

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetMediaOwnership(t *testing.T) {
	for _, tc := range []struct {
		name, id string
		partner  int
		accepted bool
	}{
		{"owned", "0_abcdefgh", 102, true},
		{"foreign partner", "0_abcdefgh", 999, false},
		{"missing partner", "0_abcdefgh", 0, false},
		{"different ID", "0_aaaaaaaa", 102, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if err := r.ParseForm(); err != nil {
					t.Error(err)
					return
				}
				var response any = Entry{ID: tc.id, PartnerID: tc.partner}
				if r.Form.Get("service") == "session" {
					response = "test-ks"
				}
				if err := json.NewEncoder(w).Encode(response); err != nil {
					t.Error(err)
				}
			}))
			defer srv.Close()
			c := NewClient(Config{ServiceURL: srv.URL, PartnerID: 102})
			defer c.HTTP().CloseIdleConnections()
			got, err := c.GetMedia(context.Background(), "0_abcdefgh")
			if tc.accepted {
				require.NoError(t, err)
				require.Equal(t, tc.id, got.ID)
			} else {
				require.Nil(t, got)
				var apiErr *APIError
				require.ErrorAs(t, err, &apiErr)
				require.Equal(t, "ENTRY_ID_NOT_FOUND", apiErr.Code)
			}
		})
	}
}
