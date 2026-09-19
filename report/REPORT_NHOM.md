# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** ILV (Nhóm 16)
**Thành viên:** Nguyễn Quốc Tuấn (Thành viên 1), [Thành viên 2], [Thành viên 3]
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và Quy định Đại học: Học bổng & Hỗ trợ Tài chính Sinh viên (K4-L3A — Trường Đại học Công nghệ, ĐHQGHN - UET)

**Tại sao nhóm chọn chủ đề này?**
Nhóm chọn chủ đề chính sách và học bổng đại học vì đây là nguồn thông tin thiết thực, thường xuyên được sinh viên tra cứu với yêu cầu độ chính xác cao về số liệu (định mức tiền thưởng, GPA yêu cầu, hồ sơ, thời hạn nộp). Dữ liệu văn bản hành chính có cấu trúc rõ ràng theo từng phần (tiêu chuẩn, quyền lợi, quy trình nộp), rất lý tưởng để đánh giá khả năng chunking theo heading và kiểm chứng tính hiệu quả của bộ lọc phân quyền đối tượng (`audience`).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Cấp học bổng KKHT kì cuối đợt xét tháng 06/2026 | https://uet.edu.vn/cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-cho-sinh-vien-tot-nghiep-dot-xet-thang-06-nam-2026/ | 2026-09-19 / 1545/QĐ-ĐHCN | 4,273 | audience: student, dept: student-affairs, cat: scholarship |
| 2 | Chương trình học bổng Đinh Thiện Lý năm học 2026-2027 | https://uet.edu.vn/chuong-trinh-hoc-bong-dinh-thien-ly-nam-hoc-2026-2027-danh-cho-sinh-vien-nam-cuoi-va-sinh-vien-nam-cuoi-co-hoan-canh-dac-biet/ | 2026-09-19 / not-stated | 6,234 | audience: student, dept: student-affairs, cat: scholarship |
| 3 | Chương trình học bổng Goertek năm 2027 | https://uet.edu.vn/chuong-trinh-hoc-bong-goertek-nam-2027/ | 2026-09-19 / 3962/ĐHQGHN-ĐT&CTSV | 3,145 | audience: student, dept: student-affairs, cat: scholarship |
| 4 | Chương trình Học bổng Tài năng Pegatron 2027 | https://uet.edu.vn/chuong-trinh-hoc-bong-tai-nang-pegatron-2027/ | 2026-09-19 / PVN-26830 | 4,816 | audience: student, dept: student-affairs, cat: scholarship |
| 5 | Đề nghị danh sách tân sinh viên nhận HB Đinh Thiện Lý 2026-2027 | https://uet.edu.vn/de-nghi-danh-sach-tan-sinh-vien-duoc-nhan-hb-dinh-thien-ly-nam-hoc-2026-2027/ | 2026-09-19 / not-stated | 2,206 | audience: student, dept: student-affairs, cat: scholarship |
| 6 | Điều chỉnh đối tượng xét học bổng Data Nest 2026-2027 | https://uet.edu.vn/dieu-chinh-doi-tuong-xet-hoc-bong-data-nest-nam-hoc-2026-2027/ | 2026-09-19 / not-stated | 3,017 | audience: student, dept: student-affairs, cat: scholarship |
| 7 | Học bổng Data Nest, năm học 2026-2027 | https://uet.edu.vn/hoc-bong-data-nest-nam-hoc-2026-2027/ | 2026-09-19 / not-stated | 4,960 | audience: student, dept: student-affairs, cat: scholarship |
| 8 | Học bổng The Best of MB Chasing 2026 | https://uet.edu.vn/hoc-bong-the-best-of-mb-chasing-2026/ | 2026-09-19 / not-stated | 2,310 | audience: student, dept: student-affairs, cat: scholarship |
| 9 | Kết quả xét chọn học bổng Vallet năm 2026 | https://uet.edu.vn/ket-qua-xet-chon-hoc-bong-vallet-danh-cho-sinh-vien-truong-dai-hoc-cong-nghe-dai-hoc-quoc-gia-ha-noi-nam-2026/ | 2026-09-19 / not-stated | 3,200 | audience: student, dept: student-affairs, cat: scholarship |
| 10 | Quy định về việc xét, cấp học bổng KKHT tại Trường ĐHCN | https://uet.edu.vn/quy-dinh-ve-viec-xet-cap-hoc-bong-khuyen-khich-hoc-tap-tai-truong-dai-hoc-cong-nghe/ | 2026-09-19 / not-stated | 3,712 | audience: staff, dept: student-affairs, cat: scholarship |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student`, `staff`, `faculty` | Phân loại nhóm đối tượng thụ hưởng nhằm lọc chính xác thông báo cho sinh viên, tránh nhiễu từ văn bản nội bộ của cán bộ/giảng viên. |
| `department` | string | `student-affairs`, `academic-affairs` | Giúp thu hẹp không gian tìm kiếm theo đơn vị phụ trách (Phòng Công tác sinh viên, Phòng Đào tạo...). |
| `category` | string | `scholarship`, `tuition`, `regulation` | Phân loại nghiệp vụ để không nhầm lẫn giữa thông báo học bổng với các quyết định học phí hay khen thưởng khác. |
| `document_version` | string | `1545/QĐ-ĐHCN`, `PVN-26830` | Định danh phiên bản văn bản hoặc số hiệu quyết định, đảm bảo tính pháp lý và kiểm chứng đối soát. |
| `retrieved_at` | string | `2026-09-19` | Ghi nhận thời điểm thu thập dữ liệu, giúp kiểm soát tính cập nhật và hiệu lực của thông báo. |
| `source_url` | string | `https://uet.edu.vn/...` | Liên kết đến bài đăng gốc công khai để người dùng hoặc kiểm thử viên đối chiếu và xác thực. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026 | FixedSizeChunker (`fixed_size`) | 4 | 1105.8 | Trung bình; chunk đều nhưng có thể cắt ngang bảng/số liệu |
| cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026 | SentenceChunker (`by_sentences`) | 3 | 1422.3 | Tốt cho câu dài, nhưng chunk hơi lớn |
| cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026 | RecursiveChunker (`recursive`) | 4 | 1066.8 | Tốt hơn fixed-size vì ưu tiên ranh giới tự nhiên |
| chuong-trinh-hoc-bong-goertek-nam-2027 | FixedSizeChunker (`fixed_size`) | 3 | 1081.7 | Chấp nhận được, nhưng dễ tách đôi hai mô hình học bổng |
| chuong-trinh-hoc-bong-goertek-nam-2027 | SentenceChunker (`by_sentences`) | 3 | 1046.0 | Khá tốt vì điều kiện/quyền lợi nằm trong câu hoàn chỉnh |
| chuong-trinh-hoc-bong-goertek-nam-2027 | RecursiveChunker (`recursive`) | 3 | 1047.0 | Tốt, giữ được đoạn theo ranh giới dòng/câu |
| chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027 | FixedSizeChunker (`fixed_size`) | 6 | 1080.7 | Trung bình; phần hồ sơ có thể bị cắt ngang |
| chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027 | SentenceChunker (`by_sentences`) | 9 | 689.9 | Tốt cho danh sách hồ sơ, chunk nhỏ hơn |
| chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027 | RecursiveChunker (`recursive`) | 6 | 1037.3 | Tốt, cân bằng giữa độ dài và ngữ cảnh |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Quốc Tuấn**
- **Loại chiến lược:** Custom heading chunker + recursive fallback
- **Mô tả & lý do chọn cho chủ đề này:** Bộ dữ liệu là các thông báo/quy định học bổng, thường có tiêu đề, đoạn điều kiện, hồ sơ, thời hạn và quyền lợi. Tôi tách theo heading để giữ mỗi mục như một đơn vị ngữ nghĩa; nếu section quá dài thì dùng `RecursiveChunker` cắt tiếp và gắn lại tiêu đề vào từng mảnh con để không mất ngữ cảnh.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def __init__(self, max_chars=1200):
        self.max_chars = max_chars
        self.fallback = RecursiveChunker(chunk_size=max_chars)

    def chunk(self, text):
        # Tách trước mỗi dòng Markdown heading.
        # Nếu một section dài quá max_chars, dùng RecursiveChunker
        # và gắn lại heading vào từng chunk con.
        ...
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Quốc Tuấn | HeadingChunker (custom + recursive fallback) | 10 / 10 | Giữ nguyên trọn vẹn tiêu đề mục, bảo toàn bảng số liệu học bổng và danh sách hồ sơ; không bị cắt cụn câu | Phụ thuộc vào chất lượng cấu trúc heading Markdown của văn bản gốc |
| [Thành viên 2] | | | | |
| [Thành viên 3] | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Với chủ đề quy định và học bổng đại học, chiến lược `HeadingChunker` kết hợp `RecursiveChunker` là tối ưu nhất. Các thông báo hành chính có cấu trúc phân tầng tự nhiên rất chặt chẽ (Tiêu chuẩn, Quyền lợi, Thành phần hồ sơ, Hạn nộp); việc phân mảnh theo heading giúp toàn bộ điều kiện và số liệu không bị cắt ngang giữa chừng, đồng thời việc gắn kèm tiêu đề mục cha vào chunk con giúp giữ trọn ngữ cảnh chủ đề khi tính toán vector embedding.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mức học bổng khuyến khích học tập kì cuối cho sinh viên loại Xuất sắc ngành CLC CNTT khóa QH-2022 là bao nhiêu? | 4.100.000 đồng/sinh viên/tháng (theo Quyết định số 1545/QĐ-ĐHCN). | `cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-thang-06-2026#1` |
| 2 | Mỗi suất học bổng Vallet năm 2026 dành cho sinh viên Trường ĐHCN trị giá bao nhiêu và lễ trao học bổng diễn ra ở đâu? | Trị giá 34.000.000 đồng; tổ chức tại Hội trường Nhà Thái Học, Văn Miếu - Quốc Tử Giám (58 Quốc Tử Giám, Hà Nội) lúc 07h30 ngày 23/08/2026. | `ket-qua-xet-chon-hoc-bong-vallet-2026#0` |
| 3 | Sinh viên cần đáp ứng những tiêu chuẩn gì về GPA, rèn luyện và ngoại ngữ để được xét chọn Học bổng Tài năng Pegatron 2027? | GPA năm học 2025-2026 từ 2.8 trở lên, kết quả rèn luyện loại Tốt trở lên, có khả năng dùng tiếng Anh/tiếng Trung và phải hoàn thành chứng chỉ tiếng Trung HSK3 trước khi thực tập tại công ty. | `chuong-trinh-hoc-bong-tai-nang-pegatron-2027#0` |
| 4 | Hồ sơ đăng ký học bổng Đinh Thiện Lý dành cho sinh viên năm cuối gồm những giấy tờ gì và hạn nộp là khi nào? | Đơn đăng ký online; bảng điểm tích lũy có xác nhận; bài luận tiếng Anh tối đa 500 từ; 1 thư giới thiệu; minh chứng NCKH/ngoại khóa; video giới thiệu <=3 phút; giấy tờ khó khăn nếu có. Hạn trước 16h30 ngày 21/7/2026. | `chuong-trinh-hoc-bong-dinh-thien-ly-nam-cuoi-2026-2027#3` |
| 5 | Chương trình học bổng Goertek năm 2027 gồm những mô hình đào tạo nào và quyền lợi của từng mô hình là gì? | Gồm 2 mô hình: đào tạo tại Việt Nam với học bổng 60 triệu đồng, gói 21.000.000 đồng/sinh viên trả 2 lần, thực tập tại Goertek Vina; đào tạo tại Trung Quốc với học bổng 80 triệu đồng, học tại Đại học Sơn Đông, miễn học phí, ký túc xá, vé máy bay khứ hồi, gói 25.000.000 đồng/sinh viên trả 2 lần. | `chuong-trinh-hoc-bong-goertek-nam-2027#0` và `#1` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mức học bổng KKHT kì cuối cho sinh viên Xuất sắc ngành CLC CNTT khóa QH-2022 | HeadingChunker | Có (Top-1, score 0.506) | Trích xuất chính xác 4.100.000 đ/tháng; có lọc metadata `audience: student` |
| 2 | Trị giá suất học bổng Vallet 2026 và địa điểm tổ chức lễ trao học bổng | HeadingChunker | Có (Top-1, score 0.346) | Đầy đủ giá trị 34.000.000 đ và địa điểm Nhà Thái Học, Văn Miếu |
| 3 | Tiêu chuẩn xét chọn Học bổng Tài năng Pegatron 2027 (GPA, rèn luyện, ngoại ngữ) | HeadingChunker | Có (Top-1, score 0.250) | Trích xuất trọn vẹn GPA 2.8, rèn luyện Tốt, ngoại ngữ HSK3 |
| 4 | Hồ sơ đăng ký học bổng Đinh Thiện Lý năm cuối và thời hạn tiếp nhận | HeadingChunker | Có (Top-1, score 0.390) | Lấy đúng chunk hồ sơ chi tiết và hạn chót 16h30 ngày 21/7/2026 |
| 5 | Các mô hình đào tạo và quyền lợi chương trình học bổng Goertek 2027 | HeadingChunker | Có (Top-1, score 0.304) | Bao quát cả 2 mô hình đào tạo tại VN (60tr) và TQ (80tr) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Lọc bằng metadata đặc biệt hữu ích ở Câu hỏi 1 và các câu hỏi tra cứu chính sách chung. Cụ thể với câu hỏi tìm kiếm mức học bổng khuyến khích học tập, nếu không có bộ lọc `metadata_filter={"audience": "student"}`, hệ thống sẽ truy xuất lẫn các văn bản quy định tổ chức của cán bộ/nhà trường (`audience: staff`). Thử nghiệm A/B trên Q1 cho thấy khi bật bộ lọc, các văn bản nội bộ bị loại bỏ hoàn toàn, giúp 100% kết quả trong top-3 đều là các quyết định học bổng sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Heading-based Chunking bảo tồn cấu trúc logic văn bản**: Khác với Fixed-size thường cắt ngang các bảng số tiền thưởng hoặc danh mục hồ sơ tại ranh giới ký tự ngẫu nhiên, HeadingChunker giữ trọn vẹn một mục hành chính hoàn chỉnh kèm tiêu đề định danh.
2. **Metadata Pre-filtering triệt tiêu xung đột vai trò (Role Collision)**: Cùng một từ khóa "học bổng", đối tượng sinh viên (`student`) và cán bộ (`staff`) áp dụng quy chế khác nhau; việc lọc trước metadata giúp thu hẹp phạm vi tìm kiếm chính xác 100%.
3. **Phân tích trường hợp lỗi (Failure Analysis)**: Khi tài liệu gốc có phần giới thiệu hoặc breadcrumbs điều hướng web quá dài, nếu không làm sạch trước thì chunk đầu tiên sẽ bị loãng từ khóa và giảm điểm tương đồng ngữ nghĩa.

**Bài học rút ra khi so sánh trong nhóm:**
Cùng một bộ dữ liệu, việc lựa chọn chiến lược chunking quyết định trực tiếp tới khả năng hiểu và trả lời của agent. Nếu chunk quá nhỏ, agent mất ngữ cảnh tiêu đề dẫn đến trả lời thiếu; nếu chunk quá lớn, vector bị loãng và giảm độ tương đồng cosine.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Nhóm sẽ xây dựng pipeline tiền xử lý (pre-processing) tự động để làm sạch hoàn toàn các thành phần giao diện web (menu, breadcrumb, footer) trước khi chunking; đồng thời bổ sung thêm metadata trường `scholarship_type` (khuyến khích / doanh nghiệp / du học) để truy xuất linh hoạt hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
