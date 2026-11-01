"""Texts of the graphical interface (English / Türkçe)."""

T = {
    # window, menus
    "app_title": ("YarnHair {v} – yarn hairiness from microscope images",
                  "YarnHair {v} – mikroskop görüntülerinden iplik tüylülüğü"),
    "menu_file": ("&File", "&Dosya"),
    "menu_lang": ("&Language", "D&il"),
    "menu_help": ("&Help", "&Yardım"),
    "act_add_images": ("Add images…", "Görüntü ekle…"),
    "act_add_folder": ("Add folder…", "Klasör ekle…"),
    "act_save": ("Save results…", "Sonuçları kaydet…"),
    "act_quit": ("Quit", "Çıkış"),
    "act_about": ("About YarnHair", "YarnHair hakkında"),
    "act_refs": ("Packing density references", "Paketleme yoğunluğu kaynakları"),
    "act_fibres": ("Fibre densities", "Lif yoğunlukları"),

    # images
    "grp_images": ("1. Images", "1. Görüntüler"),
    "label": ("Label (sample):", "Etiket (numune):"),
    "label_hint": ("applies to images added next", "bundan sonra eklenen görüntülere uygulanır"),
    "sub_as_label": ("When adding a folder, use sub-folder names as labels",
                     "Klasör eklerken alt klasör adlarını etiket yap"),
    "btn_add_images": ("Add images…", "Görüntü ekle…"),
    "btn_add_folder": ("Add folder…", "Klasör ekle…"),
    "btn_remove": ("Remove selected", "Seçileni çıkar"),
    "btn_clear": ("Clear", "Temizle"),
    "col_label": ("Label", "Etiket"),
    "col_file": ("File", "Dosya"),
    "n_images": ("{n} image(s)", "{n} görüntü"),
    "img_filter": ("Images (*.bmp *.png *.tif *.tiff *.jpg *.jpeg)", "Görüntüler (*.bmp *.png *.tif *.tiff *.jpg *.jpeg)"),

    # pixel size
    "grp_pixel": ("2. Pixel size", "2. Piksel boyutu"),
    "pixel_size": ("Pixel size at the yarn plane:", "İplik düzleminde piksel boyutu:"),
    "um_per_px": ("µm/pixel", "µm/piksel"),
    "btn_calibrate": ("Measure on a stage micrometer image…", "Mikrometre görüntüsünden ölç…"),
    "pixel_manual": ("Entered by hand.", "Elle girildi."),
    "pixel_calc": ("{L} µm ÷ {p} pixels = {s} µm/pixel ({f})",
                   "{L} µm ÷ {p} piksel = {s} µm/piksel ({f})"),

    # yarn and boundary
    "grp_yarn": ("3. Yarn and body boundary", "3. İplik ve gövde sınırı"),
    "count": ("Yarn count:", "İplik numarası:"),
    "system": ("Spinning system:", "Eğirme sistemi:"),
    "blend": ("Blend (by mass) – include the core of core-spun yarns:",
              "Karışım (kütlece) – özlü iplikte özü de ekleyin:"),
    "col_fibre": ("Fibre", "Lif"),
    "col_share": ("%", "%"),
    "col_density": ("Density g/cm³", "Yoğunluk g/cm³"),
    "col_source": ("Source", "Kaynak"),
    "btn_add_fibre": ("+ Fibre", "+ Lif"),
    "btn_del_fibre": ("– Remove", "– Çıkar"),
    "blend_total": ("Total {s} %", "Toplam %{s}"),
    "blend_rho": ("ρ = 1 / Σ(wᵢ/ρᵢ) = {r} g/cm³", "ρ = 1 / Σ(wᵢ/ρᵢ) = {r} g/cm³"),
    "blend_bad": ("Shares must add up to 100 %.", "Paylar toplamı %100 olmalı."),
    "mode_theory": ("I enter the packing density – the diameter is calculated from count and blend",
                    "Paketleme yoğunluğunu ben girerim – çap numara ve karışımdan hesaplanır"),
    "packing": ("Packing density φ:", "Paketleme yoğunluğu φ:"),
    "packing_src": ("Default 0.32: cross-sections of a cotton/elastane core-spun ring yarn (Erbil et al. 2022).",
                    "Varsayılan 0,32: pamuk/elastan özlü ring ipliği kesitleri (Erbil ve ark. 2022)."),
    "btn_refs": ("Literature…", "Literatür…"),
    "theory_calc": ("d = √(4·T / (1000·π·φ·ρ)) = √(4·{T} / (1000·π·{phi}·{rho})) mm = {d} µm",
                    "d = √(4·T / (1000·π·φ·ρ)) = √(4·{T} / (1000·π·{phi}·{rho})) mm = {d} µm"),
    "mode_measured": ("I enter a measured diameter – the packing density is calculated and checked",
                      "Ölçülmüş çapı ben girerim – paketleme yoğunluğu hesaplanır ve denetlenir"),
    "diameter": ("Diameter:", "Çap:"),
    "dtype": ("Measured on:", "Ölçüldüğü yer:"),
    "dtype_cross_section": ("Cross-section (envelope, equal-area circle)", "Kesit (dış zarf, eşdeğer daire)"),
    "dtype_optical": ("Optical side view (Uster 2DØ, microscope edge to edge)",
                      "Optik yandan görünüş (Uster 2DØ, mikroskopta kenardan kenara)"),
    "dtype_other": ("Other", "Diğer"),
    "measured_calc": ("φ = 4·T / (1000·π·d²·ρ) = 4·{T} / (1000·π·{d}²·{rho}) = {phi}",
                      "φ = 4·T / (1000·π·d²·ρ) = 4·{T} / (1000·π·{d}²·{rho}) = {phi}"),
    "measured_nocalc": ("Enter count and blend to check the diameter against packing density.",
                        "Çapı paketleme yoğunluğuyla denetlemek için numara ve karışımı girin."),
    "boundary_note": ("Body boundary = larger of this diameter and the apparent diameter of each frame.",
                      "Gövde sınırı = bu çap ile her karenin görünür çapından büyük olanı."),
    "need_count": ("Enter the yarn count.", "İplik numarasını girin."),
    "need_diameter": ("Enter the measured diameter.", "Ölçülmüş çapı girin."),

    # packing checks
    "chk_ok": ("φ = {phi}: within the references for this case ({low}–{high}).",
               "φ = {phi}: bu durumdaki kaynakların aralığında ({low}–{high})."),
    "chk_ok_noref": ("φ = {phi}: no reference of this kind; only physical limits checked.",
                     "φ = {phi}: bu türde kaynak yok; yalnız fiziksel sınırlar denetlendi."),
    "chk_notice": ("φ = {phi} differs from the references for this case ({low}–{high}). Check count, blend and diameter.",
                   "φ = {phi}, bu durumdaki kaynaklardan ({low}–{high}) farklı. Numara, karışım ve çapı kontrol edin."),
    "chk_warning": ("φ = {phi} is above the densest packing of round fibres (0.907); possible only with flattened fibres. Check the values.",
                    "φ = {phi}, yuvarlak liflerin en sıkı dizilimini (0,907) aşıyor; ancak yassılmış liflerle mümkün. Değerleri kontrol edin."),
    "chk_error": ("φ = {phi} ≥ 1 is physically impossible: the fibres would not fit into this diameter.",
                  "φ = {phi} ≥ 1 fiziksel olarak imkânsız: lifler bu çapa sığmaz."),
    "dlg_check_title": ("Check the packing density", "Paketleme yoğunluğunu kontrol edin"),
    "btn_fix": ("Correct the values", "Değerleri düzelt"),
    "btn_use_measured": ("Use this diameter", "Bu çapı kullan"),
    "btn_use_theory": ("Use the theoretical diameter (φ = {phi})", "Teorik çapı kullan (φ = {phi})"),
    "btn_continue": ("Continue", "Devam et"),

    # run
    "grp_run": ("4. Run", "4. Çalıştır"),
    "workers": ("Parallel processes:", "Paralel işlem:"),
    "workers_hint": ("each needs about 1 GB of memory", "her biri yaklaşık 1 GB bellek kullanır"),
    "save_overlays": ("Save checking images to:", "Kontrol görüntülerini şuraya kaydet:"),
    "btn_choose": ("Choose…", "Seç…"),
    "btn_start": ("Start", "Başlat"),
    "btn_stop": ("Stop", "Durdur"),
    "status_ready": ("Ready.", "Hazır."),
    "status_running": ("{done}/{total} frames, about {eta} left", "{done}/{total} kare, kalan yaklaşık {eta}"),
    "status_done": ("Finished: {ok} frame(s), {fail} could not be processed.",
                    "Bitti: {ok} kare, {fail} kare işlenemedi."),
    "status_stopped": ("Stopped.", "Durduruldu."),
    "no_images": ("Add images first.", "Önce görüntü ekleyin."),
    "frame_failed": ("{f}: could not be processed ({e})", "{f}: işlenemedi ({e})"),

    # results
    "tab_results": ("Results", "Sonuçlar"),
    "tab_summary": ("Summary per label", "Etikete göre özet"),
    "tab_overlay": ("Checking image", "Kontrol görüntüsü"),
    "res_note": ("Per 10 mm of yarn. Double-click a row to see its checking image.",
                 "10 mm iplik başına. Kontrol görüntüsü için satıra çift tıklayın."),
    "h_label": ("Label", "Etiket"), "h_frame": ("Frame", "Kare"),
    "h_N": ("N (hairs)", "N (tüy)"), "h_L": ("L (mm)", "L (mm)"),
    "h_N05": ("≥0.5 mm", "≥0,5 mm"), "h_N1": ("≥1 mm", "≥1 mm"), "h_N2": ("≥2 mm", "≥2 mm"), "h_N3": ("≥3 mm", "≥3 mm"),
    "h_mlen": ("Mean length (mm)", "Ort. uzunluk (mm)"), "h_unres": ("Unresolved", "Bağlanamayan"),
    "h_app": ("Apparent diameter (µm)", "Görünür çap (µm)"), "h_bnd": ("Boundary diameter (µm)", "Sınır çapı (µm)"),
    "h_n": ("Frames", "Kare"),
    "ov_legend": ("Dashed white: body boundary · colours: counted hairs with their connection · red: unresolved fragments",
                  "Kesikli beyaz: gövde sınırı · renkler: sayılan tüyler ve gövdeye bağlantıları · kırmızı: bağlanamayan parçalar"),
    "btn_fit": ("Fit", "Sığdır"),
    "ov_none": ("No checking image yet.", "Henüz kontrol görüntüsü yok."),

    # saving
    "save_filter": ("Excel workbook (*.xlsx);;Tab-separated text (*.tsv)",
                    "Excel çalışma kitabı (*.xlsx);;Sekmeyle ayrılmış metin (*.tsv)"),
    "saved": ("Saved: {p}", "Kaydedildi: {p}"),
    "no_results": ("There are no results to save.", "Kaydedilecek sonuç yok."),
    "sheet_frames": ("Frames", "Kareler"), "sheet_summary": ("Summary", "Özet"), "sheet_settings": ("Settings", "Ayarlar"),
    "set_version": ("YarnHair version", "YarnHair sürümü"),
    "set_date": ("Date", "Tarih"),
    "set_pixel": ("Pixel size (µm/pixel)", "Piksel boyutu (µm/piksel)"),
    "set_pixel_how": ("Pixel size source", "Piksel boyutunun kaynağı"),
    "set_count": ("Yarn count", "İplik numarası"),
    "set_tex": ("Linear density (tex)", "Doğrusal yoğunluk (tex)"),
    "set_system": ("Spinning system", "Eğirme sistemi"),
    "set_blend": ("Blend (fibre, %, g/cm³)", "Karışım (lif, %, g/cm³)"),
    "set_rho": ("Blend density (g/cm³)", "Karışım yoğunluğu (g/cm³)"),
    "set_mode": ("Body boundary", "Gövde sınırı"),
    "set_phi": ("Packing density", "Paketleme yoğunluğu"),
    "set_d": ("Boundary diameter used (µm)", "Kullanılan sınır çapı (µm)"),
    "set_dtype": ("Diameter measured on", "Çapın ölçüldüğü yer"),
    "set_config": ("Algorithm parameters", "Algoritma parametreleri"),

    # calibration dialog
    "cal_title": ("Pixel size from a stage micrometer", "Mikrometreden piksel boyutu"),
    "cal_open": ("Open micrometer image…", "Mikrometre görüntüsü aç…"),
    "cal_hint": ("Take the micrometer image with the same objective, zoom and camera resolution as the yarn images. "
                 "Click two scale lines that are far apart (mouse wheel: zoom; right button: move). A third click starts again.",
                 "Mikrometre görüntüsünü iplik görüntüleriyle aynı objektif, büyütme ve kamera çözünürlüğünde çekin. "
                 "Ölçekte birbirinden uzak iki çizgiye tıklayın (tekerlek: yakınlaştır; sağ tuş: kaydır). Üçüncü tık yeniden başlatır."),
    "cal_length": ("True distance between the two marks:", "İki işaret arasındaki gerçek uzunluk:"),
    "cal_pixels": ("Distance in the image: {p} pixels", "Görüntüdeki uzaklık: {p} piksel"),
    "cal_result": ("Pixel size = {L} µm ÷ {p} pixels = {s} µm/pixel", "Piksel boyutu = {L} µm ÷ {p} piksel = {s} µm/piksel"),
    "cal_need": ("Click two points.", "İki noktaya tıklayın."),

    # dialogs
    "refs_title": ("Packing density in the literature", "Literatürde paketleme yoğunluğu"),
    "refs_intro": ("The value depends on where the yarn edge is drawn. Your value is compared only with references of the same kind; "
                   "rows used for the current check are highlighted. ≈: read from a bar chart.",
                   "Değer, iplik kenarının nereden çizildiğine bağlıdır. Sizin değeriniz yalnız aynı türdeki kaynaklarla karşılaştırılır; "
                   "şu anki denetimde kullanılan satırlar vurgulanmıştır. ≈: çubuk grafikten okundu."),
    "kind_cross_section": ("Cross-section (envelope)", "Kesit (dış zarf)"),
    "kind_optical": ("Optical diameter (Uster 2DØ)", "Optik çap (Uster 2DØ)"),
    "kind_effective": ("Effective diameter (Liberec)", "Etkin çap (Liberec)"),
    "kind_coil_winding": ("Coil winding (compressed yarn)", "Bobine sarım (sıkıştırılmış iplik)"),
    "pending": ("source to be verified", "kaynak doğrulanacak"),
    "blend_hint": ("Knows the blend density already? Choose “Other”, 100 % and type it.",
                   "Karışım yoğunluğunu biliyorsanız “Diğer”, %100 seçip yazın."),
    "h_kind": ("Kind", "Tür"), "h_system": ("System", "Sistem"), "h_fibre": ("Fibre", "Lif"),
    "h_tex": ("tex", "tex"), "h_phi": ("φ", "φ"), "h_src": ("Source", "Kaynak"),
    "fibres_title": ("Fibre densities used by YarnHair", "YarnHair'in kullandığı lif yoğunlukları"),
    "fibres_intro": ("Only fibres with a density from a source that was read are listed. Use “Other” for any other fibre.",
                     "Yalnız yoğunluğu okunmuş bir kaynaktan alınan lifler listelenir. Diğer lifler için “Diğer”i seçin."),
    "about_text": ("<b>YarnHair {v}</b><br>Rule-based measurement of yarn hairiness from microscope images.<br><br>"
                   "Licence: MIT. Please cite the software (CITATION.cff or the Zenodo DOI of the release) and the article "
                   "describing its first application.<br><br>The code was written with the help of a large language model "
                   "(Claude, Anthropic); images are processed only by the rule-based code.",
                   "<b>YarnHair {v}</b><br>Mikroskop görüntülerinden kural tabanlı iplik tüylülüğü ölçümü.<br><br>"
                   "Lisans: MIT. Lütfen yazılıma (CITATION.cff ya da sürümün Zenodo DOI'si) ve ilk uygulamasını anlatan "
                   "makaleye atıf yapın.<br><br>Kod bir büyük dil modelinin (Claude, Anthropic) yardımıyla yazıldı; görüntüler "
                   "yalnız kural tabanlı kodla işlenir."),

    # packing density from cross-sections (YarnSection), link from YarnHair
    "menu_tools": ("&Tools", "&Araçlar"),
    "act_sections": ("Packing density from cross-sections (YarnSection)…",
                     "Kesitlerden paketleme yoğunluğu (YarnSection)…"),
    "btn_from_sections": ("From cross-sections…", "Kesitlerden…"),
    "phi_src_hand": ("entered by hand", "elle girildi"),
    "phi_src_sections": ("cross-sections of {label}: n = {n}, φ = {phi} ± {sd} (mean ± SD)",
                         "{label} kesitleri: n = {n}, φ = {phi} ± {sd} (ortalama ± SS)"),
    "set_phi_src": ("Packing density source", "Paketleme yoğunluğunun kaynağı"),
    "s_title": ("YarnSection {v} – packing density from yarn cross-sections",
                "YarnSection {v} – iplik kesitlerinden paketleme yoğunluğu"),
    "s_grp_images": ("1. Cross-section images", "1. Kesit görüntüleri"),
    "s_grp_yarns": ("3. Yarns: count and blend of each label", "3. İplikler: her etiketin numarası ve karışımı"),
    "s_btn_edit_yarn": ("Count and blend…", "Numara ve karışım…"),
    "s_col_count": ("Count", "Numara"), "s_col_blend": ("Blend", "Karışım"),
    "s_col_rho": ("ρ (g/cm³)", "ρ (g/cm³)"), "s_col_af": ("Fibre area (µm²)", "Lif alanı (µm²)"),
    "s_col_phi": ("φ", "φ"), "s_col_use": ("Use", "Kullan"),
    "s_yarn_title": ("Yarn of label {label}", "{label} etiketinin ipliği"),
    "s_yarn_missing": ("not defined – double-click", "tanımlı değil – çift tıklayın"),
    "s_fibre_area": ("Fibre area in a section = 1000·T/ρ = 1000·{T}/{rho} = {a} µm² (diameter at φ = 0.32: {d} µm).",
                     "Kesitteki lif alanı = 1000·T/ρ = 1000·{T}/{rho} = {a} µm² (φ = 0,32 için çap: {d} µm)."),
    "s_hint": ("Click around the yarn body to draw its outline: around the outermost fibres that still belong to the "
               "compact body; leave protruding and displaced fibres outside. Click on an edge to insert a point, drag a "
               "point to move it. Backspace: remove the last point · Delete: the point under the mouse · Ctrl+Z: undo · "
               "wheel: zoom · right button: move the image.",
               "İplik gövdesinin çevresine tıklayarak sınırını çizin: sıkı gövdeye hâlâ ait olan en dıştaki liflerin "
               "çevresinden; sapan ve yerinden oynamış lifleri dışarıda bırakın. Kenara tıklamak araya nokta ekler, "
               "noktayı sürükleyerek taşıyın. Backspace: son noktayı sil · Delete: faredeki noktayı sil · Ctrl+Z: geri al · "
               "tekerlek: yakınlaştır · sağ tuş: görüntüyü kaydır."),
    "s_btn_suggest": ("Suggest outline", "Sınır öner"),
    "s_btn_undo": ("Undo", "Geri al"),
    "s_btn_clear_outline": ("Clear outline", "Sınırı sil"),
    "s_btn_prev": ("◀ Previous", "◀ Önceki"),
    "s_btn_next": ("Next ▶", "Sonraki ▶"),
    "s_use": ("Use this section", "Bu kesiti kullan"),
    "s_suggest_none": ("No outline could be suggested; draw it by hand.", "Sınır önerilemedi; elle çizin."),
    "s_suggest_done": ("Suggested outline: check that it runs around the outermost fibres of the compact body. Accept "
                       "it, move its points, or draw the outline yourself. A suggestion that is not confirmed is not "
                       "used in the mean.",
                       "Önerilen sınır: sıkı gövdenin en dıştaki liflerinin çevresinden geçip geçmediğine bakın. "
                       "Kabul edin, noktalarını taşıyın ya da sınırı kendiniz çizin. Onaylanmayan öneri ortalamaya "
                       "girmez."),
    "s_btn_accept": ("Accept suggestion", "Öneriyi kabul et"),
    "s_btn_draw": ("I will draw it", "Kendim çizeceğim"),
    "s_accepted": ("Suggestion accepted.", "Öneri kabul edildi."),
    "s_draw_hint": ("Draw the outline: click around the compact body. Ctrl+Z brings the suggestion back; "
                    "Suggest outline makes a new one.",
                    "Sınırı çizin: sıkı gövdenin çevresine tıklayın. Ctrl+Z öneriyi geri getirir; Sınır öner yeniden "
                    "önerir."),
    "st_none": ("No outline", "Sınır yok"),
    "st_suggested": ("Suggested – not confirmed", "Önerildi – onaylanmadı"),
    "st_accepted": ("Suggestion accepted", "Öneri kabul edildi"),
    "st_edited": ("Suggestion corrected", "Öneri düzeltildi"),
    "st_manual": ("Drawn by hand", "Elle çizildi"),
    "s_col_status": ("Outline", "Sınır"),
    "note_pending": ("not confirmed – not in the mean", "onaylanmadı – ortalamada yok"),
    "s_pending_warn": (" {n} suggestion(s) of this label are not confirmed and are not in the mean.",
                       " Bu etiketin {n} önerisi onaylanmadı, ortalamaya girmedi."),
    "set_status": ("Outline status", "Sınır durumu"),
    "set_status_text": ("suggested = automatic suggestion not confirmed (left out of the mean); accepted = suggestion "
                        "confirmed unchanged; edited = suggestion corrected by the user; manual = drawn by hand",
                        "suggested = onaylanmamış otomatik öneri (ortalamaya girmez); accepted = değiştirilmeden "
                        "kabul edilen öneri; edited = kullanıcının düzelttiği öneri; manual = elle çizilen sınır"),
    "s_live": ("A = {a} µm² · d = {d} µm · aspect {asp}", "A = {a} µm² · d = {d} µm · en/boy {asp}"),
    "s_live_phi": (" · φ = {phi}", " · φ = {phi}"),
    "s_need_points": ("Outline: {n} point(s); at least 3 are needed.", "Sınır: {n} nokta; en az 3 gerekir."),
    "s_err_cross": ("The outline crosses itself: move the points so that it does not.",
                    "Sınır kendini kesiyor: noktaları kesişmeyecek şekilde taşıyın."),
    "s_phi_impossible": ("φ ≥ 1 is impossible: check the outline, the pixel size and the count.",
                         "φ ≥ 1 imkânsız: sınırı, piksel boyutunu ve numarayı kontrol edin."),
    "s_flag_aspect": ("Aspect above {lim}: oblique or flattened section? With the short axis φ = {phim}.",
                      "En/boy {lim} üstünde: eğik ya da ezik kesit mi? Kısa eksenle φ = {phim}."),
    "s_no_image": ("Add cross-section images (File menu or the buttons on the left).",
                   "Kesit görüntüsü ekleyin (Dosya menüsü ya da soldaki düğmeler)."),
    "s_missing_image": ("Image not found: {p}", "Görüntü bulunamadı: {p}"),
    "s_tab_sections": ("Sections", "Kesitler"),
    "s_tab_summary": ("Summary per label", "Etikete göre özet"),
    "h_image": ("Image", "Görüntü"), "h_pts": ("Points", "Nokta"), "h_area": ("Area (µm²)", "Alan (µm²)"),
    "h_deq": ("d (µm)", "d (µm)"), "h_major": ("Long axis (µm)", "Uzun eksen (µm)"),
    "h_minor": ("Short axis (µm)", "Kısa eksen (µm)"), "h_aspect": ("Aspect", "En/boy"),
    "h_phim": ("φ (short axis)", "φ (kısa eksen)"), "h_use": ("Use", "Kullan"), "h_note": ("Note", "Not"),
    "h_status": ("Outline", "Sınır"), "h_pending": ("Not confirmed", "Onay bekleyen"),
    "h_origin": ("Accepted / corrected / drawn", "Kabul / düzeltilen / çizilen"),
    "h_nsec": ("Sections", "Kesit"), "h_phi_mean": ("φ mean ± SD", "φ ort. ± SS"),
    "h_ci": ("95 % CI of the mean", "Ortalamanın %95 GA'sı"), "h_cv": ("CV %", "DK %"),
    "h_deq_mean": ("d mean ± SD (µm)", "d ort. ± SS (µm)"), "h_flagged": ("Flagged", "İşaretli"),
    "h_dth": ("Diameter in YarnHair (µm)", "YarnHair'deki çap (µm)"),
    "note_aspect": ("aspect > {lim}", "en/boy > {lim}"),
    "s_sum_note": ("Mean of the sections marked “Use”; suggestions that are not confirmed are left out. The diameter "
                   "is what YarnHair calculates from count, blend and the mean φ. Add sections if the confidence "
                   "interval is wider than ±0.02.",
                   "“Kullan” işaretli kesitlerin ortalaması; onaylanmamış öneriler dışarıda kalır. Çap, YarnHair'in "
                   "numara, karışım ve ortalama φ'den hesapladığı değerdir. Güven aralığı ±0,02'den genişse kesit "
                   "ekleyin."),
    "s_btn_use_phi": ("Use φ of the selected label in YarnHair", "Seçili etiketin φ'sini YarnHair'de kullan"),
    "s_need_three": ("At least 3 sections of this label are needed.", "Bu etiketten en az 3 kesit gerekir."),
    "s_used_phi": ("φ = {phi} ({label}, {n} sections) is now set in YarnHair.",
                   "φ = {phi} ({label}, {n} kesit) YarnHair'e aktarıldı."),
    "s_act_open": ("Open outlines…", "Sınırları aç…"),
    "s_act_save_outlines": ("Save outlines…", "Sınırları kaydet…"),
    "s_act_save_checks": ("Save checking images…", "Kontrol görüntülerini kaydet…"),
    "s_act_method": ("Method", "Yöntem"),
    "s_act_about": ("About YarnSection", "YarnSection hakkında"),
    "s_act_close": ("Close", "Kapat"),
    "s_outline_filter": ("YarnSection outlines (*.json)", "YarnSection sınırları (*.json)"),
    "s_saved_outlines": ("Outlines saved: {p}. From now on every change is saved to this file.",
                         "Sınırlar kaydedildi: {p}. Bundan sonra her değişiklik bu dosyaya kaydedilir."),
    "s_autosaved": ("Saved: {p}", "Kaydedildi: {p}"),
    "s_ask_save": ("The outlines have not been saved. Save them before closing?",
                   "Sınırlar kaydedilmedi. Kapatmadan önce kaydedilsin mi?"),
    "s_open_failed": ("The file could not be opened: {e}", "Dosya açılamadı: {e}"),
    "s_no_sections": ("No outlined section yet.", "Henüz sınırı çizilmiş kesit yok."),
    "s_checks_done": ("{n} checking image(s) saved in {p}", "{n} kontrol görüntüsü kaydedildi: {p}"),
    "s_status": ("{n} image(s), {m} with an outline, {p} not confirmed",
                 "{n} görüntü, {m} tanesinde sınır var, {p} tanesi onay bekliyor"),
    "sheet_sections": ("Sections", "Kesitler"), "sheet_yarns": ("Yarns", "İplikler"),
    "set_method": ("Method", "Yöntem"),
    "set_method_text": ("φ = fibre area / area inside the outline; fibre area = 1000·T/ρ (µm², T in tex, ρ in g/cm³); "
                        "outline drawn around the compact yarn body",
                        "φ = lif alanı / sınırın içindeki alan; lif alanı = 1000·T/ρ (µm², T tex, ρ g/cm³); "
                        "sınır sıkı iplik gövdesinin çevresinden çizildi"),
    "set_aspect_limit": ("Aspect limit for flagging", "İşaretleme için en/boy sınırı"),
    "s_method_html": (
        "<h3>Packing density from cross-sections</h3>"
        "<p>The outline of the yarn body is drawn on each section: around the outermost fibres that still belong to "
        "the compact body; protruding and displaced fibres stay outside. The fibre area of a section perpendicular to "
        "the yarn axis follows from count and blend alone:</p>"
        "<p style='margin-left:20px'>A<sub>f</sub> = 1000·T/ρ &nbsp;(µm²; T in tex, ρ in g/cm³)</p>"
        "<p>because the mass per unit length equals the density times the fibre area in a transverse section. Fibre "
        "fineness, fibre number and twist do not enter, and no fibre has to be recognised in the image. The packing "
        "density of a section is φ = A<sub>f</sub>/A, with A the area inside the outline; d is the diameter of the "
        "circle of the same area.</p>"
        "<p><b>Checks.</b> Aspect = long/short axis of the ellipse with the same second moments as the outline. An "
        "oblique cut lengthens the outline by 1/cos(angle) (20° → 6 % more area, φ 6 % lower) and leaves the short "
        "axis unchanged; flattening by the knife also raises the aspect. Sections above 1.3 are flagged, and φ "
        "calculated with the short axis is shown for them. Untick “Use” to leave a section out of the mean.</p>"
        "<p><b>Sections.</b> Embed the yarn under the same light tension as in the images to be measured (a relaxed "
        "elastane core-spun yarn bulks). Cut perpendicular to the yarn axis. A lost core (hole) does not matter: it "
        "lies inside the outline and its mass is in T. Take 15–20 sections per yarn from different places; the "
        "confidence interval of the mean is shown in the summary.</p>"
        "<p><b>Suggestion.</b> When an image without an outline is opened, an outline is suggested: the fibres are "
        "found by their edges (or by their grey level), the gaps between them are closed and the largest compact "
        "region is taken. Check it and choose <b>Accept suggestion</b>, move its points, or <b>I will draw it</b>. "
        "A suggestion that is not confirmed is not used in the mean; the summary counts accepted, corrected and "
        "hand-drawn outlines. The suggestion follows the compact body of well-cut sections; it takes in spread "
        "fibres and fails on loosely packed or damaged sections, so look at every one.</p>",
        "<h3>Kesitlerden paketleme yoğunluğu</h3>"
        "<p>Her kesitte iplik gövdesinin sınırı çizilir: sıkı gövdeye hâlâ ait olan en dıştaki liflerin çevresinden; "
        "sapan ve yerinden oynamış lifler dışarıda kalır. İplik eksenine dik bir kesitteki lif alanı yalnız numara ve "
        "karışımdan gelir:</p>"
        "<p style='margin-left:20px'>A<sub>f</sub> = 1000·T/ρ &nbsp;(µm²; T tex, ρ g/cm³)</p>"
        "<p>çünkü birim uzunluktaki kütle, yoğunluk ile enine kesitteki lif alanının çarpımıdır. Lif inceliği, lif "
        "sayısı ve büküm hesaba girmez; görüntüde lif tanımak gerekmez. Kesitin paketleme yoğunluğu φ = "
        "A<sub>f</sub>/A'dır; A sınırın içindeki alan, d aynı alanlı dairenin çapıdır.</p>"
        "<p><b>Denetimler.</b> En/boy = sınırla aynı ikinci momentlere sahip elipsin uzun/kısa ekseni. Eğik kesit "
        "sınırı 1/cos(açı) kadar uzatır (20° → alan %6 fazla, φ %6 düşük), kısa ekseni değiştirmez; bıçağın ezmesi "
        "de en/boyu artırır. 1,3'ü aşan kesitler işaretlenir ve kısa eksenle hesaplanan φ gösterilir. Bir kesiti "
        "ortalamadan çıkarmak için “Kullan” işaretini kaldırın.</p>"
        "<p><b>Kesit alma.</b> İpliği ölçülecek görüntülerdeki gibi hafif gergin gömün (gevşek elastanlı özlü iplik "
        "kabarır). İplik eksenine dik kesin. Özün düşmesi (boşluk) sorun değildir: sınırın içinde kalır ve kütlesi "
        "T'nin içindedir. İplik başına farklı yerlerden 15–20 kesit alın; ortalamanın güven aralığı özette "
        "gösterilir.</p>"
        "<p><b>Öneri.</b> Sınırı olmayan bir görüntü açılınca sınır önerilir: lifler kenarlarından (ya da gri "
        "düzeylerinden) bulunur, aralarındaki boşluklar kapatılır ve en büyük sıkı bölge alınır. Bakın ve "
        "<b>Öneriyi kabul et</b>'i seçin, noktalarını taşıyın ya da <b>Kendim çizeceğim</b>'i seçin. Onaylanmayan "
        "öneri ortalamaya girmez; özet kabul edilen, düzeltilen ve elle çizilen sınırları sayar. Öneri iyi alınmış "
        "kesitlerde sıkı gövdeyi izler; yayılmış lifleri içine alır, gevşek ya da bozuk kesitlerde bulamaz; bu "
        "yüzden her birine bakın.</p>"),
    "s_about_text": ("<b>YarnSection {v}</b> (part of YarnHair)<br>Packing density of yarns from the outline of "
                     "cross-sections and the yarn count.<br><br>Licence: MIT. Please cite the software (CITATION.cff or "
                     "the Zenodo DOI of the release).<br><br>The code was written with the help of a large language "
                     "model (Claude, Anthropic); images are processed only by the rule-based code.",
                     "<b>YarnSection {v}</b> (YarnHair'in parçası)<br>İplik kesitlerinin sınırından ve iplik "
                     "numarasından paketleme yoğunluğu.<br><br>Lisans: MIT. Lütfen yazılıma atıf yapın (CITATION.cff "
                     "ya da sürümün Zenodo DOI'si).<br><br>Kod bir büyük dil modelinin (Claude, Anthropic) yardımıyla "
                     "yazıldı; görüntüler yalnız kural tabanlı kodla işlenir."),
}


def tr(key, lang, **kw):
    en, trk = T[key]
    s = trk if lang == "tr" else en
    return s.format(**kw) if kw else s


def fmt(x, nd, lang):
    """Number with nd decimals; decimal comma in Turkish."""
    s = f"{x:.{nd}f}"
    return s.replace(".", ",") if lang == "tr" else s


def fmt_dur(seconds, lang):
    m = int(round(seconds / 60))
    if m < 1:
        return "<1 dk" if lang == "tr" else "<1 min"
    if m < 60:
        return f"{m} dk" if lang == "tr" else f"{m} min"
    h, m = divmod(m, 60)
    return f"{h} sa {m} dk" if lang == "tr" else f"{h} h {m} min"
