-- Do the PDFs have a text layer? Born-digital PDFs make OCR comparisons uninformative.
SELECT
    count(*)                                                      AS pdfs,
    sum(pages)                                                    AS pages,
    count(*) FILTER (error IS NOT NULL)                           AS unreadable,
    count(*) FILTER (low_text_pages = pages)                      AS image_only,
    count(*) FILTER (low_text_pages > 0)                          AS with_some_low_text_pages,
    sum(low_text_pages)                                           AS low_text_pages,
    median(median_chars_per_page)::INT                            AS median_chars_per_page
FROM text_layer;
