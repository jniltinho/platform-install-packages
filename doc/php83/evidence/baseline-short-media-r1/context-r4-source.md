# Explicit READY transcoded context probe, source-supported rationale

Root's original-asset no-GET observation returned sources0/flavor_assets0/actions0/messages0; overall failed UNDRAINED_TAIL. Later zero known-pattern matches do not convert that to full context privacy PASS. No claim is made that the following source analysis establishes the actual reason for the empty response.

Pinned original Rigel source:
- kContextDataHelper.php SHA356c1e82939919e0797154a47916ad68c7292d2777620f1edd6f735d3f1fa001,267–293 includes explicit selected asset when permitted; ALL_TAGS314–317 passes it through. No universal isOriginal exclusion here.
- kPlaybackContextDataHelper.php SHA7d7ec74448fb4161dabe3ebf02e0be5ee9ae07e0e3c69e1c97c08bb0305eaaab,381–386 filters flavors per delivery protocol; APPLE_HTTP501–506 priorities applembr, then ipadnew/iphonenew/h265/dash, then ipad/iphone.532–550 keeps matching tags.739–748 subsequently removes flavors not present in generated playback sources, so no sources can result in no returned flavors without proving no initial asset.
- assetParams.php constant TAG_APPLEMBR='applembr',line71.
- deployment/base/scripts/init_data/04.flavorParams.ini SHA34857a5d5cb06d18a3c0fda3e18cca813a201b7cfc97266429934eb7452fc7c2: source id0 tags=source; params2/3/4 include matching ipadnew/iphonenew/dash tags. asset.php703–708 copies profile tags when constructing assets. This is source intent, not an observation of actual stored tags.

Smallest next source-supported observation chooses existing READY nonoriginal asset0_21p06l2j/params2 (root's observed metadata); no conversion/profile edits. NEW playback_context_r4.observe(call,private_url,asset_row) validates known exact IDs/parameter join, partner102, entry0_wzmt2sfy, status2, version2, nonoriginal false flag, MP4 and short size bound before issuing the single native API request. Root selects params2; the library's finite allowed set also recognizes the other two already observed READY assets, not arbitrary assets.

Optional tags from the same already available asset object yield only selected_hls_tag_match=true/false; missing tags return null, never inferred from INI or extra API calls. Native source tags are comma-split exact values. Matching tags are eligibility evidence only, not proof an active HLS delivery profile exists. All R3 response-shape/enrollment/incomplete-coverage guards remain; source URL is never fetched/exported. Empty source result remains an observation, not failure repair or playback success.

Author14 pure tests PASS. R1/R2/R3 remain preserved. Independent review and actual CLI outcomes separate; root exclusively operates VM.
