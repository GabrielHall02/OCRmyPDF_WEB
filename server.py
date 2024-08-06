import os
import tempfile
import streamlit as st
import ocrmypdf

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

STATE_FIXED_PDF_PATH = "fixed_pdf_path"
STATE_UPLOADED_FILE = "uploaded_file"
STATE_UPLOADED_FILE_NAME = "uploaded_file_name"
STATE_SIDECAR_PATH = "sidecar_path"

ocrmypdf_ocr = False
ocrmypdf_remove_background = False
ocrmypdf_deskew = False
ocrmypdf_optimize = 1

st.set_page_config(page_title="OCRmyPDF")


def uploader_callback():
    if st.session_state[STATE_UPLOADED_FILE] is not None:
        fd, path = tempfile.mkstemp()

        with st.spinner(
            "For large files, the duration of the process can be very long. Therefore, it is recommended to be patient and wait as long as no error message is displayed."
        ):
            try:
                with os.fdopen(fd, "wb") as tmp:
                    uploaded_file = st.session_state[STATE_UPLOADED_FILE]

                    tmp.write(uploaded_file.getvalue())
                    tmp.close()

                    fixed_path = path + "_fixed.pdf"
                    sidecar_path = path + ".txt" if output_text_file else None

                    ocrmypdf.ocr(
                        path,
                        fixed_path,
                        language=language,
                        sidecar=sidecar_path,
                        remove_background=ocrmypdf_remove_background,
                        optimize=ocrmypdf_optimize,
                        deskew=ocrmypdf_deskew,
                        tesseract_timeout=400 if ocrmypdf_ocr else 0,
                        skip_text=True,
                        max_image_mpixels=901167396,
                        image_dpi=72,
                        invalidate_digital_signatures=invalidate_digital_signatures,
                    )

                    st.session_state[STATE_FIXED_PDF_PATH] = fixed_path
                    st.session_state[STATE_UPLOADED_FILE_NAME] = (
                        uploaded_file.name + "_ompow.pdf"
                    )
                    if sidecar_path:
                        st.session_state[STATE_SIDECAR_PATH] = sidecar_path
            finally:
                os.remove(path)


def download_callback():
    for key in st.session_state.keys():
        del st.session_state[key]


c1 = st.container()
c1.title("OCRmyPDF")

if STATE_FIXED_PDF_PATH not in st.session_state:
    c1.write(
        "Select options and upload PDF. Once this process is successfully completed, the edited PDF file will be available for download."
    )
    ocrmypdf_ocr = c1.checkbox("Optical character recognition (OCR)", value=True)
    language = c1.multiselect("Language", ["eng", "tur", "por"])
    ocrmypdf_remove_background = c1.checkbox("Remove background")
    ocrmypdf_deskew = c1.checkbox("Deskew")
    output_text_file = c1.checkbox("Output text file")
    invalidate_digital_signatures = c1.checkbox("Invalidate digital signatures")
    ocrmypdf_optimize = c1.slider(
        label="Optimize file size (0 off, 1 without quality loss, 3 smallest but maybe with slight quality loss)",
        min_value=0,
        max_value=3,
        value=0,
    )
    c1.file_uploader(
        label="Upload PDF", on_change=uploader_callback, key=STATE_UPLOADED_FILE
    )

else:
    c1.write(
        "Editing of the PDF file has been successfully completed. Now the optimized version is ready for download."
    )
    try:
        with open(st.session_state[STATE_FIXED_PDF_PATH], "rb") as f:
            c1.download_button(
                label="Download PDF",
                data=f,
                file_name=st.session_state[STATE_UPLOADED_FILE_NAME],
                on_click=download_callback,
            )
        if STATE_SIDECAR_PATH in st.session_state:
            with open(st.session_state[STATE_SIDECAR_PATH], "rb") as f:
                c1.download_button(
                    label="Download Sidecar Text File",
                    data=f,
                    file_name=st.session_state[STATE_UPLOADED_FILE_NAME].replace(
                        ".pdf", ".txt"
                    ),
                    on_click=download_callback,
                )
    finally:
        os.remove(st.session_state[STATE_FIXED_PDF_PATH])
        if STATE_SIDECAR_PATH in st.session_state:
            os.remove(st.session_state[STATE_SIDECAR_PATH])
