# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Quốc Tuấn
**Nhóm:** Nhóm 16
**Ngày:** 19/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần giống nhau, nên hai đoạn văn bản có khả năng nói về cùng một ý nghĩa hoặc cùng một chủ đề. Giá trị càng gần 1 thì mức độ tương đồng ngữ nghĩa càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần nộp hồ sơ học bổng trước ngày hết hạn.
- Câu B: Người học phải gửi đơn xin học bổng đúng thời hạn quy định.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng đều nói về yêu cầu nộp hồ sơ/đơn học bổng đúng hạn.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên cần nộp hồ sơ học bổng trước ngày hết hạn.
- Câu B: Thư viện mở cửa từ 8 giờ sáng đến 5 giờ chiều.
- Tại sao khác: Một câu nói về học bổng và hạn nộp hồ sơ, câu còn lại nói về thời gian hoạt động của thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine similarity tập trung vào hướng của vector, tức là quan hệ ngữ nghĩa, thay vì bị ảnh hưởng nhiều bởi độ lớn của vector. Với text embeddings, hai câu có thể cùng nghĩa dù độ dài hoặc cường độ biểu diễn khác nhau, nên so sánh theo góc thường phù hợp hơn khoảng cách Euclid.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Phép tính theo công thức:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`

Kiểm tra bằng `FixedSizeChunker` cũng cho kết quả `23` chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Khi overlap tăng lên 100, bước nhảy còn `500 - 100 = 400`, nên số chunk là `ceil((10000 - 100) / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, giảm nguy cơ cắt mất thông tin quan trọng, nhưng đổi lại số chunk tăng và retrieval/embedding tốn tài nguyên hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Tôi strip văn bản đầu vào, trả về `[]` nếu text rỗng, rồi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu câu nhưng vẫn giữ dấu câu trong từng sentence. Sau đó tôi gom tối đa `max_sentences_per_chunk` câu vào mỗi chunk và strip khoảng trắng thừa. Edge case còn hạn chế là các chữ viết tắt như `TS.`, `v.v.` hoặc số thập phân có thể bị hiểu nhầm là ranh giới câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Tôi tách văn bản theo thứ tự separator từ lớn đến nhỏ: đoạn trắng, xuống dòng, câu, khoảng trắng, rồi ký tự. Nếu một mảnh vẫn dài hơn `chunk_size`, hàm `_split` gọi đệ quy với danh sách separator còn lại; sau đó các mảnh nhỏ được gom lại để chunk không bị vụn. Base case là text rỗng, text đã ngắn hơn `chunk_size`, không còn separator, hoặc separator cuối là chuỗi rỗng thì cắt cứng theo `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Tôi dùng in-memory store để lưu mỗi `Document` thành một record gồm `id`, `content`, bản copy của `metadata` và vector embedding. Khi thêm tài liệu, nếu metadata chưa có `doc_id` thì tự gán theo `doc.id` để các chunk vẫn truy vết được về tài liệu gốc. Khi search, query được embed rồi so sánh với từng record bằng dot product; vì embedding đã chuẩn hoá nên dot product tương đương cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Tôi lọc metadata trước rồi mới chạy similarity search, để `top_k` không bị chiếm bởi tài liệu sai điều kiện lọc. Với `delete_document`, tôi xoá tất cả record có `metadata["doc_id"]` hoặc `id` trùng với `doc_id` cần xoá, rồi trả về `True` nếu số record giảm và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Agent lấy `top_k` chunk liên quan từ `EmbeddingStore`, nếu không có kết quả thì trả lời rằng không tìm thấy thông tin phù hợp và không gọi LLM. Với kết quả tìm được, tôi dựng prompt có phần ngữ cảnh được đánh số `[1]`, `[2]`, `[3]` kèm nguồn từ metadata, đồng thời yêu cầu chỉ dựa trên ngữ cảnh được cung cấp để hạn chế bịa thông tin.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
Checkpoint 4:
.venv/bin/python -m pytest tests/ -v

============================= test session starts ==============================
platform darwin -- Python 3.11.14, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên có thành tích học tập xuất sắc được nhận học bổng khuyến khích. | Người học đạt kết quả học tập xuất sắc được cấp học bổng khen thưởng. | cao | 0.386 | Đúng |
| 2 | Mức học bổng Vallet dành cho sinh viên là 34 triệu đồng mỗi suất. | Học bổng Goertek hỗ trợ sinh viên gói kinh phí lên đến 80 triệu đồng. | cao | 0.223 | Đúng |
| 3 | Hồ sơ đăng ký học bổng gồm bảng điểm tích lũy và bài luận tiếng Anh. | Hạn chót tiếp nhận hồ sơ xin học bổng là trước 16h30 ngày 21 tháng 7. | thấp | 0.136 | Đúng |
| 4 | Sinh viên nộp đơn xin học bổng khuyến khích tại phòng công tác sinh viên. | Thư viện trường mở cửa phục vụ bạn đọc từ thứ hai đến thứ sáu hàng tuần. | thấp | 0.000 | Đúng |
| 5 | Sinh viên bị kỷ luật cảnh cáo không đủ điều kiện xét cấp học bổng. | Sinh viên có thành tích rèn luyện xuất sắc được ưu tiên xét nhận học bổng. | thấp | 0.154 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Kết quả bất ngờ nhất là ở **Cặp 5**: về mặt ngữ nghĩa logic, hai câu có điều kiện hoàn toàn trái ngược nhau (bị kỷ luật không được nhận vs rèn luyện xuất sắc được ưu tiên), nhưng điểm tương đồng (0.154) vẫn cao hơn Cặp 3 (0.136) và lớn hơn hẳn Cặp 4 (0.000). Điều này cho thấy các biểu diễn embedding/vector không gian dựa trên từ vựng thường gom cụm văn bản theo trường chủ đề bề mặt (đều chứa các từ khóa như 'sinh viên', 'học bổng', 'xét') mà chưa phản ánh được tính phủ định hay quan hệ logic phân cực nếu không dùng các mô hình ngôn ngữ sâu (dense semantic embeddings).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mức học bổng khuyến khích học tập kì cuối cho sinh viên loại Xuất sắc ngành CLC CNTT khóa QH-2022 là bao nhiêu? | `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026#1`: Căn cứ Quyết định 1545/QĐ-ĐHCN, mức học bổng KKHT loại Xuất sắc ngành CLC CNTT khóa QH-2022 là 4.100.000 đồng/sinh viên/tháng. | 0.506 | Có | Mức học bổng khuyến khích học tập loại Xuất sắc ngành CLC CNTT khóa QH-2022 là 4.100.000 đồng/sinh viên/tháng (theo Quyết định số 1545/QĐ-ĐHCN). |
| 2 | Mỗi suất học bổng Vallet năm 2026 dành cho sinh viên Trường ĐHCN trị giá bao nhiêu và lễ trao học bổng diễn ra ở đâu? | `ket-qua-xet-chon-hoc-bong-vallet-2026#0`: Thông báo kết quả học bổng Vallet 2026 trị giá 34.000.000 đồng/suất, lễ trao diễn ra lúc 07h30 ngày 23/08/2026 tại Hội trường Nhà Thái Học, Văn Miếu – Quốc Tử Giám. | 0.346 | Có | Mỗi suất học bổng Vallet trị giá 34.000.000 đồng; lễ trao học bổng được tổ chức tại Hội trường Nhà Thái Học, Văn Miếu – Quốc Tử Giám lúc 07h30 ngày 23/08/2026. |
| 3 | Sinh viên cần đáp ứng những tiêu chuẩn gì về GPA, rèn luyện và ngoại ngữ để được xét chọn Học bổng Tài năng Pegatron 2027? | `chuong-trinh-hoc-bong-tai-nang-pegatron-2027#0`: Điều kiện xét học bổng Pegatron 2027 gồm GPA năm 2025-2026 từ 2.8 trở lên, kết quả rèn luyện loại Tốt trở lên, có khả năng tiếng Anh/Trung, hoàn thành chứng chỉ tiếng Trung HSK3. | 0.250 | Có | Sinh viên cần GPA năm học 2025-2026 từ 2.8 trở lên, rèn luyện loại Tốt trở lên, có khả năng sử dụng tiếng Anh/Trung và hoàn thành chứng chỉ tiếng Trung HSK3 trước khi thực tập. |
| 4 | Hồ sơ đăng ký học bổng Đinh Thiện Lý dành cho sinh viên năm cuối gồm những giấy tờ gì và hạn nộp là khi nào? | `chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027#3`: Hồ sơ gồm đơn online, bảng điểm tích lũy, bài luận tiếng Anh <=500 từ, thư giới thiệu, minh chứng, video <=3 phút. Hạn trước 16h30 ngày 21/7/2026. | 0.390 | Có | Hồ sơ gồm đơn đăng ký online, bảng điểm xác nhận, bài luận tiếng Anh <=500 từ, 1 thư giới thiệu, minh chứng ngoại khóa, video <=3 phút; hạn nộp trước 16h30 ngày 21/7/2026. |
| 5 | Chương trình học bổng Goertek năm 2027 gồm những mô hình đào tạo nào và quyền lợi của từng mô hình là gì? | `chuong-trinh-hoc-bong-goertek-nam-2027#0`: Gồm mô hình đào tạo tại VN (học bổng 60 triệu, gói 21.000.000đ trả 2 lần) và đào tạo tại TQ (học bổng 80 triệu, học ĐH Sơn Đông, miễn học phí, KTX, vé máy bay, gói 25 triệu). | 0.304 | Có | Chương trình gồm 2 mô hình: 1) Đào tạo tại VN: học bổng 60 triệu đồng, hỗ trợ 21 triệu trả 2 lần; 2) Đào tạo tại TQ: học bổng 80 triệu đồng, học tại ĐH Sơn Đông, miễn học phí, KTX, vé máy bay khứ hồi. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (100% câu hỏi đều có chunk chứa đúng thông tin trả lời ở vị trí Top-1).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
Qua quá trình chạy đối sánh và demo, tôi nhận thấy chiến lược `HeadingChunker` kết hợp `RecursiveChunker` của tôi phát huy tối đa ưu thế trên dữ liệu văn bản hành chính/quy định nhờ giữ nguyên tiêu đề mục cha kèm nội dung bảng số liệu. So với `FixedSizeChunker` hay cắt vụn văn bản ở ranh giới ký tự ngẫu nhiên khiến câu trả lời bị cụt, `HeadingChunker` duy trì tính toàn vẹn ngữ cảnh rất cao. Ngoài ra, việc kết hợp metadata pre-filter (`audience: student`) là chìa khóa để triệt tiêu hoàn toàn các văn bản nội bộ dành cho cán bộ/giảng viên lọt vào kết quả của sinh viên.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
