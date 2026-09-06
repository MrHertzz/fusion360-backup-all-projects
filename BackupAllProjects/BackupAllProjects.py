"""
BackupAllProjects.py
---------------------
Fusion 360 Data Panel'indeki TÜM projelerdeki TÜM tasarım dosyalarını
yerel diske .f3d (Fusion Archive) ve isteğe bağlı .step formatında export eder.

KULLANIM:
1. Fusion 360'ı aç.
2. Üstteki menüden: UTILITIES (Yardımcı Programlar) > ADD-INS > Scripts and Add-Ins
   (veya Shift+S kısayolu)
3. "Scripts" sekmesinde yeşil "+" ikonuna tıkla, bu dosyanın olduğu klasörü seç.
4. Listeden "BackupAllProjects" seçip "Run" de.
5. Açılan pencerede yedeklerin kaydedileceği klasörü seç.
6. Script tüm projeleri tarayıp export eder, ilerlemeyi text komut penceresinde görürsün.

NOTLAR:
- Sadece "aktif" (senin erişimin olan) projeleri tarar.
- Alt klasörleri (nested folders) de gezer.
- Zaten export edilmiş bir dosya varsa, üzerine yazmaz (atlar) - script'i tekrar
  çalıştırıp kaldığın yerden devam edebilirsin.
- Büyük projelerde (100+ dosya) işlem uzun sürebilir, Fusion'ı kapatma.
- Öğrenci lisansı ile herhangi bir kısıtlama olmadan çalışır, sadece kendi
  hesabındaki dosyalara erişebilirsin.
"""

import adsk.core
import adsk.fusion
import traceback
import os
import re


def sanitize_filename(name):
    """Dosya adındaki geçersiz karakterleri temizler."""
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()


def export_document_version(app, ui, data_file, target_folder, export_step, log):
    """Tek bir DataFile'ı .f3d (ve isteğe bağlı .step) olarak export eder."""
    doc = None
    try:
        safe_name = sanitize_filename(data_file.name)
        f3d_path = os.path.join(target_folder, safe_name + ".f3d")
        step_path = os.path.join(target_folder, safe_name + ".step")

        need_f3d = not os.path.exists(f3d_path)
        need_step = export_step and not os.path.exists(step_path)

        if not need_f3d and not need_step:
            log(f"  [ATLANDI - zaten var] {safe_name}")
            return True

        # Dosyayı arka planda aç
        doc = app.documents.open(data_file, True)
        if doc is None:
            log(f"  [HATA] Açılamadı: {safe_name}")
            return False

        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            log(f"  [ATLANDI - Fusion design değil] {safe_name}")
            return False

        export_mgr = design.exportManager

        if need_f3d:
            archive_options = export_mgr.createFusionArchiveExportOptions(f3d_path)
            export_mgr.execute(archive_options)
            log(f"  [OK] .f3d -> {f3d_path}")

        if need_step:
            step_options = export_mgr.createSTEPExportOptions(step_path, design.rootComponent)
            export_mgr.execute(step_options)
            log(f"  [OK] .step -> {step_path}")

        return True

    except Exception:
        log(f"  [HATA] {data_file.name}: {traceback.format_exc(limit=1)}")
        return False
    finally:
        if doc is not None:
            try:
                doc.close(False)  # kaydetmeden kapat
            except Exception:
                pass


def walk_folder(app, ui, folder, target_root, export_step, log, path_prefix=""):
    """Bir DataFolder içindeki tüm dosyaları ve alt klasörleri gezer."""
    current_path = os.path.join(target_root, path_prefix)
    os.makedirs(current_path, exist_ok=True)

    for data_file in folder.dataFiles:
        # Sadece Fusion design dosyalarını al (fileExtension boşsa genelde Fusion design'dır)
        export_document_version(app, ui, data_file, current_path, export_step, log)

    for sub_folder in folder.dataFolders:
        safe_sub = sanitize_filename(sub_folder.name)
        walk_folder(app, ui, sub_folder, target_root, export_step,
                    log, os.path.join(path_prefix, safe_sub))


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Hedef klasörü kullanıcıya seçtir
        folder_dlg = ui.createFolderDialog()
        folder_dlg.title = "Yedeklerin kaydedileceği klasörü seç"
        result = folder_dlg.showDialog()
        if result != adsk.core.DialogResults.DialogOK:
            ui.messageBox("İşlem iptal edildi.")
            return
        target_root = folder_dlg.folder

        # STEP de export edilsin mi?
        answer = ui.messageBox(
            "Her dosya için ek olarak .STEP formatında da export edilsin mi?\n"
            "(Sadece geometri, başka CAD programlarında açmak içindir)",
            "STEP Export",
            adsk.core.MessageBoxButtonTypes.YesNoButtonType,
            adsk.core.MessageBoxIconTypes.QuestionIconType
        )
        export_step = (answer == adsk.core.DialogResults.DialogYes)

        # Basit log dosyası + text komut penceresi
        log_path = os.path.join(target_root, "backup_log.txt")
        log_file = open(log_path, "a", encoding="utf-8")

        def log(msg):
            print(msg)
            log_file.write(msg + "\n")
            log_file.flush()

        log("=== Fusion 360 Toplu Yedekleme Başladı ===")

        all_projects = app.data.dataProjects
        total_projects = all_projects.count
        log(f"Toplam proje sayısı: {total_projects}")

        for i in range(total_projects):
            project = all_projects.item(i)
            safe_proj_name = sanitize_filename(project.name)
            log(f"\n--- Proje: {project.name} ---")
            root_folder = project.rootFolder
            walk_folder(app, ui, root_folder, target_root, export_step, log, safe_proj_name)

        log("\n=== Tamamlandı ===")
        log_file.close()

        ui.messageBox(f"Yedekleme tamamlandı!\n\nKlasör: {target_root}\n\nDetaylar için backup_log.txt dosyasına bak.")

    except Exception:
        if ui:
            ui.messageBox(f"Beklenmeyen hata:\n{traceback.format_exc()}")
