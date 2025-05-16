# Uploads Directory

This directory is used to store uploaded files, such as images and documents that are processed by the OCR service.

## Purpose

- Temporary storage for uploaded files before processing
- Mounted to the backend service container at `/app/uploads`
- Used by the OCR service to extract text from images and documents

## Notes

- This directory should be excluded from version control (except for this README)
- In a production environment, consider using a more robust storage solution like S3 or a dedicated file server
