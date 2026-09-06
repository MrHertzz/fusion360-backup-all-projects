# Fusion 360 Backup All Projects

Autodesk Fusion 360'ın Data Panel'inde bulunan **tüm projelerdeki tüm tasarım dosyalarını** tek seferde tarayıp `.f3d` (Fusion Archive) ve isteğe bağlı `.step` formatında yerel diskine indiren bir Fusion 360 script'i.

Fusion 360, projeleri buluta kaydettiği için "klasörü kopyala" gibi klasik bir yedekleme yapılamaz. Bu script, Fusion'ın kendi Python API'sini kullanarak bu işlemi otomatikleştirir — özellikle **öğrenci lisansı** gibi süresi dolabilen hesaplarda düzenli yedek almak için kullanışlıdır.

## Özellikler

- Data Panel'deki **tüm projeleri** ve içindeki **alt klasörleri** (nested folders) otomatik olarak gezer
- Her tasarım dosyasını:
  - `.f3d` (Fusion Archive) — tam tasarım geçmişi (feature timeline), parametreler, sketch'ler dahil
  - `.step` (isteğe bağlı) — sadece geometri, başka CAD programlarında (SolidWorks vb.) açmak için
- Proje adına göre **klasör klasör** organize eder (`HedefKlasör/ProjeAdı/DosyaAdı.f3d`)
- Daha önce export edilmiş dosyaları **atlar** — yarıda kesilse bile script'i tekrar çalıştırıp kaldığın yerden devam edebilirsin
- İşlem sonunda `backup_log.txt` dosyasına detaylı log yazar

## Gereksinimler

- Autodesk Fusion 360 (herhangi bir lisans türü — öğrenci, ücretsiz, ticari)
- Windows veya macOS

## Kurulum

1. Bu repoyu indir/klonla.
2. `BackupAllProjects` klasörünü olduğu gibi bırak — içindeki `.py` ve `.manifest` dosyalarını ayırma, Fusion script'i klasör yapısına göre tanıyor.
3. Fusion 360'ı aç, klavyeden **Shift + S** bas (veya üstteki **UTILITIES** / **ARAÇLAR** sekmesinden **Scripts and Add-Ins**'e git).
4. **Scripts** sekmesinde yeşil **+** ikonuna tıkla, `BackupAllProjects` klasörünü seç.
5. Listeden **BackupAllProjects**'i seç, **Run** de.

## Kullanım

1. Script çalıştığında önce yedeklerin kaydedileceği **hedef klasörü** seçmeni ister.
2. Ardından `.step` formatında da export edilip edilmeyeceğini sorar (yalnızca Fusion'da açacaksan gerek yok).
3. Tüm projeleri tarar, ilerlemeyi Fusion'ın text komut penceresinde ve `backup_log.txt` dosyasında gösterir.
4. Bittiğinde bir onay mesajı çıkar.

## Bilinen Sınırlamalar

- **Assembly / linkli bileşenler:** Bir montaj dosyası başka dosyalara link veriyorsa, her parça ayrı ayrı export edilir ama linkler otomatik yeniden kurulmaz. Yeni bir hesaba upload ederken aynı klasör yapısını korumak gerekir.
- **Cloud-only veriler taşınmaz:** Yorum geçmişi, sürüm (version) geçmişi, paylaşım/collaboration bilgisi, simulation/generative design sonuçları `.f3d` içine dahil olmaz.
- Script sadece erişimin olan projeleri tarar.

## Sorun Giderme

**`AttributeError: 'Application' object has no attribute 'exportManager'`**
Bu hata, eski API kullanımından kaynaklanır. Bu repodaki güncel script, `exportManager`'ı doğru şekilde `design.exportManager` üzerinden çağırır — script'in en güncel halini kullandığından emin ol.

## Lisans

Kişisel kullanım için serbestçe düzenlenebilir ve dağıtılabilir.
