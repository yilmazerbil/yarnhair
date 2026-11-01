# YarnHair

Türkçe | [English](README.md)

Mikroskop görüntülerinden kural tabanlı iplik tüylülüğü ölçümü; grafik arayüzlü
program (Türkçe/İngilizce) ve komut satırı.

YarnHair, koyu zemin üzerinde parlak görünen düz bir iplik parçasının mikroskop
görüntüsünde iplikten çıkan lifleri (tüyleri) bulur ve 10 mm iplik başına şunları
verir:

| sütun | anlamı |
|---|---|
| `N` | tüy sayısı |
| `L` | iplik gövdesi dışındaki toplam tüy uzunluğu (mm) |
| `N05`, `N1`, `N2`, `N3` | ucu gövde sınırından 0,5, 1, 2 ve 3 mm uzağa ulaşan tüy sayısı |
| `mean_length` | ortalama tüy uzunluğu (mm) |
| `unresolved` | gövdeye bağlanamayan lif parçaları (sayılmaz) |

`L`, Uster tüylülük indeksi H'nin tanımını izler (gövdeden çıkan toplam lif
uzunluğu, alt mesafe eşiği yok). `N1`, ASTM D5647'de tercih edilen 1 mm ölçüm
yüksekliğine karşılık gelir.

## Yöntemin kuralları

1. **Her tüy iplik gövdesine bağlıdır.** Bir parça ancak gövde sınırına
   bağlanabiliyorsa sayılır: sınıra 40 pikselden yakın bitiyorsa doğrudan,
   değilse lif (sırt) haritası üzerinden en düşük maliyetli yolla; bu yolun
   çoğu lif üzerinde olmalı ve uzunluğu boşluğun 1,6 katı + 30 pikseli
   geçmemelidir. Bağlantı tüy uzunluğuna eklenir. Bağlanamayan parçalar
   `unresolved` olarak raporlanır.
2. **Tüy uzunluğu gövde dışındaki uzunluktur**; lif boyunca uçtan gövde sınırına
   kadar ölçülür, köprülenen görünmeyen bölümler dahildir.
3. **Gövde sınırı teorik iplik çapından dar olamaz.** Sınır yarıçapı = en
   büyüğü(teorik yarıçap, görünür yarı yükseklik yarıçapı). Teorik çap iplik
   numarası, lif (karışım) yoğunluğu ve paketleme yoğunluğundan hesaplanır
   (varsayılan 0,32; bkz. *Paketleme yoğunluğunun seçimi*).
4. **Hiçbir mesafe eşiği tüyü kesmez.** Kısa ya da ipliğe neredeyse paralel
   tüyler de sayılır; 0,5/1/2/3 mm sınıfları ayrıca verilir.
5. **Tespit parlaklıkla değil çizgi biçimiyle yapılır**: çok ölçekli sırt
   filtresi (Sato, σ = 1–3 piksel) ve histerezis eşikleme; yaygın parlak
   bölgeler tüy sayılmaz.
6. Kıvrılan uçlar ve ilmekler kapandıkları tüye aittir; kesişen tüyler, lifin
   kavşaktan düz devam ettiği yönde ayrılır.

Ayrıntılar ve tüm parametreler (İngilizce): [docs/method.md](docs/method.md).

## Grafik arayüzlü program

**Releases** sayfasından bilgisayarınıza uygun zip dosyasını indirin
(Apple M serisi işlemcili Mac'ler için `YarnHair-macOS-AppleSilicon.zip`, Intel
işlemcili Mac'ler için `YarnHair-macOS-Intel.zip`, ya da `YarnHair-Windows.zip`),
açın ve **YarnHair**'e çift tıklayın. Başka bir şey
kurmanız gerekmez. Programlar imzalı olmadığı için sistem bir kez sorar:

- macOS: "YarnHair açılamıyor…" → **Sistem Ayarları → Gizlilik ve Güvenlik** →
  YarnHair iletisinin yanındaki **Yine de Aç**.
- Windows: "Windows bilgisayarınızı korudu" → **Ek bilgi** → **Yine de çalıştır**.

Dil **Dil** menüsünden seçilir (English / Türkçe). Pencere bir ölçümün dört
adımını izler:

1. **Görüntüler** — görüntü dosyaları ya da klasör ekleyin; her görüntünün bir
   etiketi (numune adı) olur. *Alt klasör adlarını etiket yap* seçiliyse
   `B0/…, B1/…` gibi bir klasör kendiliğinden etiketlenir.
2. **Piksel boyutu** — iplik düzlemindeki µm/piksel değerini yazın ya da aynı
   büyütmede çekilmiş bir objektif mikrometresi görüntüsünü açıp ölçeğin iki
   noktasına tıklayın ve aradaki uzunluğu yazın (ör. 1000 µm); program hesabı
   gösterir (µm ÷ piksel).
3. **İplik ve gövde sınırı** — iplik numarası (tex, Ne, Nm, dtex ya da denye),
   eğirme sistemi ve karışım. Her lifi listeden seçip kütlece payını yazın;
   yoğunluğu ve kaynağı kendiliğinden gelir (Yardım → Lif yoğunlukları).
   Listede olmayan lif: *Diğer*'i seçip yoğunluğu yazın. Özlü ipliklerde özü de
   karışıma ekleyin. Sonra ya
   - **paketleme yoğunluğunu girin** (varsayılan 0,32): teorik çap hesaplanır, ya da
   - **ölçülmüş çapı girin** (kesitten ya da optik yan görüntüden): paketleme
     yoğunluğu hesaplanır ve denetlenir.

   Paketleme yoğunluğu, programda kayıtlı literatür değerleriyle (Yardım →
   Paketleme yoğunluğu kaynakları) aynı ölçüm türü ve eğirme sistemi için
   karşılaştırılır; sonuç girişlerin altında renkli gösterilir. 1 ve üstü
   fiziksel olarak imkânsızdır, kullanılamaz. 0,907'nin (yuvarlak liflerin en
   sıkı yerleşimi) üstündeki ya da eşleşen kaynakların aralığından 0,05'ten
   fazla sapan bir değerde **Başlat**, değerleri düzeltmeyi, değeri yine de
   kullanmayı ya da (ölçülmüş çapta) teorik çapı kullanmayı sorar.
4. **Çalıştır** — kareler paralel işlemlerde ölçülür (her biri yaklaşık 1 GB
   bellek kullanır); kontrol görüntüleri bir klasöre kaydedilebilir.

Sonuçlar kare kare (bir satıra çift tıklayınca kontrol görüntüsü açılır) ve
etiket başına ortalama ± SS olarak gösterilir. **Dosya → Sonuçları kaydet**,
Excel çalışma kitabı (kareler, etikete göre özet, tüm ayarlar ve hesaplar) ya da
sekmeyle ayrılmış metin dosyası yazar.

## Kaynak koddan kurulum

Kodu indirin (yeşil **Code** düğmesi → **Download ZIP** ya da bir sürümün
arşivi), açın ve o klasörde şunu çalıştırın:

```bash
pip install .            # yalnız komut satırı
pip install ".[gui]"     # grafik arayüzlü programla (PySide6, openpyxl)
yarnhair-gui             # grafik programı başlat
```

Python ≥ 3.9. Yayımlanan değerler numpy 2.2.6, scipy 1.15.3 ve scikit-image
0.25.2 ile birebir elde edildi (`packaging/requirements-app.txt`; indirilen
programlar da bu sürümlerle hazırlanır); daha yeni sürümler `L`'de binde birkaç
fark verebilir.

## Komut satırı

```bash
# Ne 14/1 pamuk ipliğinin teorik çapı (yoğunluk 1,52 g/cm3)
yarnhair --lang tr diameter --ne 14 --density 1.52
# -> 332.3   (paketleme yoğunluğu 0,32; --packing 0.6 ile: 242.7)

# lif listesinden karışım yoğunluğu (kütlece paylar)
yarnhair --lang tr diameter --tex 42.18 --blend cotton=50,lyocell=25,pla=25
# -> 341.7

# bir ipliğin tüm karelerini ölç; sonuçları results.tsv dosyasına ekle;
# kontrol görüntülerini kaydet
yarnhair --lang tr measure kareler/B0/*.bmp --label B0 --diameter-um 331 \
         --pixel-um 3.85 --out results.tsv --overlay-dir kontrol
```

Python içinden:

```python
from yarnhair import measure_frame
res, tuyler, baglanamayan, ayrinti = measure_frame("kare.bmp", diameter_um=331, pixel_um=3.85)
print(res["N"], res["L"])
```

`yarnhair defaults` varsayılan parametreleri yazdırır; `--config '{"hi": 18}'`
ile değiştirilebilir.

### Dil

İki arayüz de Türkçe ve İngilizcedir. Komut satırı: `yarnhair --lang tr ...` ya
da `YARNHAIR_LANG=tr` ortam değişkeni (varsayılan: sistem dili, değilse
İngilizce). Komut ve seçenek adları (`measure`, `--out` vb.), çıktı dosyasındaki
sütun adları ve metin dosyalarının veri biçimi (ondalık nokta) iki dilde de
aynıdır. Metin dosyasını Türkçe Excel'de açarken *Veri > Metinden/CSV'den* ile
ondalık ayırıcıyı nokta seçin (programın Excel çıktısında buna gerek yoktur).

## Giriş görüntüleri

- Koyu zemin üzerinde parlak görünen, yaklaşık yatay, düz bir iplik parçası.
- İplik düzleminde bilinen piksel boyutu, ör. objektif mikrometresinden.
- Yayımlanan analizde 2592 × 1944 piksel, 3,85 µm/piksel kareler (kare başına
  ≈ 10 mm iplik), iplik başına en az 1 m arayla alınmış 25 kare kullanıldı.
- Eşikler bu düzenek için elle çizilmiş dört kareye göre ayarlandı. Başka
  mikroskop, büyütme ya da aydınlatmada önce birkaç elle çizilmiş karede kontrol
  edin.

## Kontrol görüntüleri

Her kare için bir kontrol görüntüsü kaydedilebilir: kesikli beyaz çizgiler gövde
sınırıdır, sayılan her tüy (gövdeye bağlantısı dahil) ayrı renkte, bağlanamayan
parçalar kırmızıdır. Görüntüde sabit bir gösterim dönüşümü (arka plan çıkarma,
sabit ölçek, gamma 0,5, keskinleştirme) kullanılır; ölçüm her zaman ham
görüntüde yapılır.

## Paketleme yoğunluğunun seçimi

Paketleme yoğunluğu φ (paketleme oranı, lif hacim oranı), iplik kesitinde
liflerin kapladığı paydır. Sabit değildir: life, eğirme sistemine ve büküme,
en çok da ipliğin kenarının nereden çizildiğine bağlıdır:

- kesit, kenar en dıştaki liflerin çevresinden: yaklaşık 0,24–0,42
  (Kilic ve ark. 2014; Demir 2023; Erbil ve ark. 2022);
- hareket eden ipliğin fotoğrafı: 0,32–0,45 (Hearle ve ark. 1969, Tablo 2.8);
- bir mile sarılarak yassılmış iplik (bobin sarma yöntemi): 0,53–0,61
  (Hearle ve ark. 1969, Tablo 2.9).

YarnHair'de gövde sınırı ipliğin dış kenarıdır; bu yüzden varsayılan bir kesit
değeridir: yayımlanan analizdeki iplik türü olan pamuk/elastan özlü ring
ipliğinde ölçülen 0,32 (Erbil ve ark. 2022). Karşılaştırılan tüm ipliklerde
aynı değeri ya da varsa her iplik için ölçülmüş değeri kullanın.

Yayımlanan analizde 0,32 yerine 0,6 kullanmak sınırı en çok %27 daraltıp tüy
sayısını ve uzunluğunu %16–29 artırdı; on ipliğin sıralaması neredeyse aynı
kaldı (Spearman ρ ≥ 0,96). Yayımlanan teorik çaplarda yalnız kesikli lif
kılıfının yoğunluğu kullanıldı (elastan öz dışarıda); programın istediği gibi
özü de katmak çapı %1'den az değiştirir.

## Çalışma süresi

Masaüstü işlemcide 5 megapiksellik kare başına yaklaşık 15–80 s. Kareler
birbirinden bağımsızdır; bellek yettiği ölçüde birkaç işlem paralel çalışır.

## Tekrarlanabilirlik

1.0.0 sürümü, aşağıdaki makalede kullanılan algoritmayı ve varsayılan
parametreleri içerir; makaledeki 275 kare değeri bu kod ve yukarıdaki kütüphane
sürümleriyle üretildi. `yarnhair-gui --selftest` (indirilen programda
`YarnHair --selftest`) yapay bir kareyi ayrı bir işlemde ölçer ve pencereyi
ekransız açar; çıkış kodu 0 ise kurulum çalışıyor demektir.

## Kaynaklar

- Demir M (2023) Exploring the relationship between yarn type and packing
  density: a study of single-ply, two-ply, and siro-spun yarns. Tekstil ve
  Mühendis 30(130):124–130. https://doi.org/10.7216/teksmuh.1320576
- Erbil Y, Islam R, Babaarslan O, Sırlıbaş S (2022) Effect of structural
  changes on the cotton composite yarn properties. J Nat Fibers 19:1899–1907.
  https://doi.org/10.1080/15440478.2020.1788687
- Hearle JWS, Grosberg P, Backer S (1969) Structural mechanics of fibers,
  yarns, and fabrics, vol 1. Wiley-Interscience, New York.
- Kilic M, Buyukbayraktar RB, Kilic GB, Aydin S, Eski N (2014) Comparing the
  packing densities of yarns spun by ring, compact and vortex spinning systems
  using image analysis method. Indian J Fibre Text Res 39:351–357.

Kayıtlı lif yoğunluklarının ve diğer paketleme yoğunluğu değerlerinin
kaynakları programda (Yardım menüsü) ve `yarnhair/fibres.py`,
`yarnhair/packing.py` dosyalarında listelenir.

## Atıf

Lütfen yazılıma (`CITATION.cff` ya da sürümün Zenodo DOI'si) ve ilk uygulamasını
anlatan makaleye atıf yapın:

> Celayir E, Erbil Y, Babaarslan O. Effect of ternary blends of cotton, hemp,
> TENCEL™, PLA, rPET and Naia™ on yarn quality, mechanical properties, air
> permeability and wettability of elastane core-spun denim weft. (gönderildi)

## Yapay zekâ kullanımı

Kod, yazarın belirlediği kurallara göre bir büyük dil modelinin (Claude,
Anthropic) yardımıyla yazıldı ve her adımda elle çizilmiş karelerle
karşılaştırılarak düzeltildi. Görüntüler yalnızca bu depodaki kural tabanlı kodla
işlenir; hiçbir üretken model görüntü ya da ölçüm üretmez veya değiştirmez.

## Lisans

MIT — bkz. [LICENSE](LICENSE).
