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
