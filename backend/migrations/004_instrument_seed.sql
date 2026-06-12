-- Migration 004: Seed Instrumen CIPP untuk MK Budaya Tiongkok
-- Jalankan di VPS:
--   docker compose exec -T db psql -U sinoku -d sinoku_db < backend/migrations/004_instrument_seed.sql

BEGIN;

-- ── CIPP Dimensions ──────────────────────────────────────────────────────────
INSERT INTO cipp_dimensions (kode, nama_dimensi, nama_id, nama_zh, deskripsi_id, urutan, warna_hex)
VALUES
  ('B', 'Context',  'Konteks',  '背景',  'Evaluasi relevansi dan kebutuhan mata kuliah Budaya Tiongkok', 1, '#3182ce'),
  ('C', 'Input',    'Masukan',  '输入',  'Evaluasi kualifikasi dosen, materi ajar, dan sumber daya', 2, '#38a169'),
  ('D', 'Process',  'Proses',   '过程',  'Evaluasi pelaksanaan perkuliahan dan interaksi pembelajaran', 3, '#d69e2e'),
  ('E', 'Product',  'Produk',   '产品',  'Evaluasi hasil belajar dan pencapaian kompetensi', 4, '#e53e3e')
ON CONFLICT (kode) DO UPDATE SET
  nama_id = EXCLUDED.nama_id,
  nama_zh = EXCLUDED.nama_zh,
  deskripsi_id = EXCLUDED.deskripsi_id,
  warna_hex = EXCLUDED.warna_hex;

-- ── Sub-Dimensi B (Context) ──────────────────────────────────────────────────
WITH dim AS (SELECT id FROM cipp_dimensions WHERE kode = 'B')
INSERT INTO cipp_sub_dimensions (dimension_id, kode, nama_id, nama_zh, urutan)
SELECT dim.id, kode, nama_id, nama_zh, urutan FROM dim, (VALUES
  ('B.1', 'Relevansi Kurikulum',          '课程相关性',       1),
  ('B.2', 'Kebutuhan dan Harapan Stakeholder', '利益相关者需求', 2),
  ('B.3', 'Dukungan Institusi',           '机构支持',         3)
) AS v(kode, nama_id, nama_zh, urutan)
ON CONFLICT (kode) DO NOTHING;

-- ── Sub-Dimensi C (Input) ────────────────────────────────────────────────────
WITH dim AS (SELECT id FROM cipp_dimensions WHERE kode = 'C')
INSERT INTO cipp_sub_dimensions (dimension_id, kode, nama_id, nama_zh, urutan)
SELECT dim.id, kode, nama_id, nama_zh, urutan FROM dim, (VALUES
  ('C.1', 'Kualifikasi dan Kompetensi Dosen', '教师资质与能力', 1),
  ('C.2', 'Materi Ajar dan Bahan Kuliah',     '教学材料',       2),
  ('C.3', 'Fasilitas dan Sarana Pembelajaran','教学设施',       3)
) AS v(kode, nama_id, nama_zh, urutan)
ON CONFLICT (kode) DO NOTHING;

-- ── Sub-Dimensi D (Process) ──────────────────────────────────────────────────
WITH dim AS (SELECT id FROM cipp_dimensions WHERE kode = 'D')
INSERT INTO cipp_sub_dimensions (dimension_id, kode, nama_id, nama_zh, urutan)
SELECT dim.id, kode, nama_id, nama_zh, urutan FROM dim, (VALUES
  ('D.1', 'Metode dan Strategi Pengajaran', '教学方法与策略', 1),
  ('D.2', 'Interaksi dan Partisipasi',      '互动与参与',     2),
  ('D.3', 'Penilaian dan Umpan Balik',      '评估与反馈',     3)
) AS v(kode, nama_id, nama_zh, urutan)
ON CONFLICT (kode) DO NOTHING;

-- ── Sub-Dimensi E (Product) ──────────────────────────────────────────────────
WITH dim AS (SELECT id FROM cipp_dimensions WHERE kode = 'E')
INSERT INTO cipp_sub_dimensions (dimension_id, kode, nama_id, nama_zh, urutan)
SELECT dim.id, kode, nama_id, nama_zh, urutan FROM dim, (VALUES
  ('E.1', 'Pencapaian Kompetensi dan CPL',  '能力达成',   1),
  ('E.2', 'Pemahaman Budaya Tiongkok',       '文化理解',   2),
  ('E.3', 'Kepuasan dan Dampak Jangka Panjang', '满意度与影响', 3)
) AS v(kode, nama_id, nama_zh, urutan)
ON CONFLICT (kode) DO NOTHING;

-- ── Items B.1 — Relevansi Kurikulum ─────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'B.1')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('B1', 1,
   'Materi MK Budaya Tiongkok yang saya ajarkan relevan dengan kebutuhan mahasiswa di era globalisasi',
   'Materi MK Budaya Tiongkok yang saya pelajari relevan dengan kebutuhan saya sebagai mahasiswa',
   '我所教授的中国文化课程内容与全球化时代学生需求高度相关',
   '我所学习的中国文化课程内容与我作为学生的需求高度相关'),
  ('B2', 2,
   'Capaian Pembelajaran (CPL) MK Budaya Tiongkok sesuai dengan tuntutan dunia kerja saat ini',
   'Capaian Pembelajaran (CPL) MK Budaya Tiongkok sesuai dengan kebutuhan saya untuk masa depan',
   '中国文化课程的学习成果符合当前职场需求',
   '中国文化课程的学习成果符合我未来的需要'),
  ('B3', 3,
   'Topik-topik yang dibahas dalam MK ini mencerminkan perkembangan budaya Tiongkok terkini',
   'Topik-topik yang dibahas dalam MK ini mencerminkan budaya Tiongkok yang relevan dengan kehidupan saya',
   '本课程涵盖的主题反映了当代中国文化的发展',
   '本课程涵盖的主题与我的生活密切相关'),
  ('B4', 4,
   'Bobot SKS MK Budaya Tiongkok sudah proporsional dengan beban materi yang harus disampaikan',
   'Bobot SKS MK Budaya Tiongkok sudah proporsional dengan materi yang saya pelajari',
   '中国文化课程的学分比重与教学内容相称',
   '中国文化课程的学分比重与我所学内容相称')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items B.2 — Kebutuhan Stakeholder ───────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'B.2')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('B5', 1,
   'MK Budaya Tiongkok mendapat dukungan yang kuat dari pimpinan program studi',
   'MK Budaya Tiongkok diakui penting oleh program studi saya',
   '中国文化课程得到专业负责人的大力支持',
   '我的专业承认中国文化课程的重要性'),
  ('B6', 2,
   'Tujuan MK Budaya Tiongkok selaras dengan visi-misi institusi dan program studi',
   'Tujuan MK Budaya Tiongkok selaras dengan tujuan studi saya di program ini',
   '中国文化课程目标与院校和专业的愿景使命一致',
   '中国文化课程目标与我在本专业的学习目标一致')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items B.3 — Dukungan Institusi ───────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'B.3')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('B7', 1,
   'Institusi menyediakan anggaran dan sumber daya yang memadai untuk pengembangan MK ini',
   'Institusi mendukung kegiatan akademik MK Budaya Tiongkok dengan baik',
   '学校为本课程的发展提供充足的预算和资源',
   '学校很好地支持中国文化课程的学术活动'),
  ('B8', 2,
   'Ada kebijakan institusi yang mendukung pengembangan kompetensi lintas budaya mahasiswa',
   'Ada program atau kegiatan institusi yang mendukung pembelajaran budaya Tiongkok saya',
   '学校有支持学生跨文化能力发展的政策',
   '学校有支持我学习中国文化的项目或活动')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items C.1 — Kualifikasi Dosen ────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'C.1')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('C1', 1,
   'Latar belakang pendidikan dan keahlian saya sesuai dengan mata kuliah yang saya ampu',
   'Dosen MK Budaya Tiongkok memiliki latar belakang pendidikan dan keahlian yang sesuai',
   '我的教育背景和专业知识与所教课程相符',
   '中国文化课程教师具有相应的教育背景和专业知识'),
  ('C2', 2,
   'Saya aktif mengikuti pelatihan atau pengembangan kompetensi terkait budaya Tiongkok',
   'Dosen MK ini terlihat terus mengembangkan kompetensinya di bidang budaya Tiongkok',
   '我积极参加与中国文化相关的培训或能力提升活动',
   '本课程教师持续提升其在中国文化领域的专业能力'),
  ('C3', 3,
   'Saya memiliki pengalaman langsung (kunjungan/riset) dengan budaya Tiongkok',
   'Dosen MK ini memiliki pengalaman langsung dengan budaya Tiongkok yang disampaikan di kelas',
   '我有直接接触中国文化的经验（访问/研究）',
   '本课程教师有直接接触中国文化的经验并在课堂上分享')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items C.2 — Materi Ajar ───────────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'C.2')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('C4', 1,
   'Bahan ajar yang saya gunakan (buku, modul, artikel) up-to-date dan relevan',
   'Bahan ajar yang digunakan dalam MK ini (buku, modul, artikel) up-to-date dan relevan',
   '我使用的教学材料（书籍、模块、文章）是最新且相关的',
   '本课程使用的教学材料（书籍、模块、文章）是最新且相关的'),
  ('C5', 2,
   'Saya menggunakan media ajar yang beragam (video, audio, presentasi) untuk memperkaya pembelajaran',
   'Dosen menggunakan media ajar yang beragam (video, audio, presentasi) sehingga pembelajaran lebih menarik',
   '我使用多种教学媒体（视频、音频、演示文稿）丰富教学',
   '教师使用多种教学媒体，使课程更加丰富有趣'),
  ('C6', 3,
   'RPS MK Budaya Tiongkok yang saya susun sudah mencakup seluruh aspek budaya yang esensial',
   'Materi perkuliahan yang diberikan sudah mencakup aspek-aspek budaya Tiongkok yang penting',
   '我编制的课程大纲涵盖了所有重要的文化方面',
   '所提供的教学材料涵盖了中国文化的重要方面')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items C.3 — Fasilitas ─────────────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'C.3')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('C7', 1,
   'Ruang kelas yang digunakan kondusif dan mendukung proses pembelajaran budaya Tiongkok',
   'Ruang kelas yang digunakan kondusif untuk pembelajaran MK Budaya Tiongkok',
   '所使用的教室环境有利于中国文化的学习',
   '所使用的教室环境适合中国文化课程的学习'),
  ('C8', 2,
   'Peralatan teknologi (proyektor, speaker, akses internet) tersedia dan berfungsi dengan baik',
   'Peralatan teknologi di kelas (proyektor, speaker, internet) berfungsi dengan baik dan mendukung pembelajaran',
   '技术设备（投影仪、音响、网络）齐全且运行良好',
   '课堂技术设备（投影仪、音响、网络）运行良好，有助于学习')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items D.1 — Metode Pengajaran ─────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'D.1')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('D1', 1,
   'Saya menggunakan metode pembelajaran yang bervariasi (ceramah, diskusi, role-play, studi kasus)',
   'Dosen menggunakan metode pembelajaran yang bervariasi sehingga kuliah tidak monoton',
   '我使用多样化的教学方法（讲授、讨论、角色扮演、案例分析）',
   '教师采用多样化的教学方法，使课程不单调'),
  ('D2', 2,
   'Saya mengaitkan materi budaya Tiongkok dengan konteks nyata dan kehidupan sehari-hari',
   'Dosen mengaitkan materi budaya Tiongkok dengan contoh nyata yang relevan dengan kehidupan sehari-hari',
   '我将中国文化材料与现实生活情境联系起来',
   '教师将中国文化内容与日常生活中的实际案例联系起来'),
  ('D3', 3,
   'Saya menyampaikan materi dengan jelas dan sistematis sesuai dengan RPS',
   'Dosen menyampaikan materi dengan jelas, runtut, dan mudah dipahami',
   '我按照课程大纲清晰、系统地讲授教学内容',
   '教师讲授清晰、有条理，易于理解'),
  ('D4', 4,
   'Saya mendorong mahasiswa untuk aktif berpikir kritis dan analitis tentang budaya Tiongkok',
   'Dosen mendorong saya untuk berpikir kritis dan menganalisis fenomena budaya Tiongkok',
   '我鼓励学生对中国文化进行积极的批判性和分析性思考',
   '教师鼓励我对中国文化现象进行批判性思考和分析')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items D.2 — Interaksi ─────────────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'D.2')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('D5', 1,
   'Saya menciptakan suasana kelas yang aktif dan mendorong mahasiswa untuk bertanya dan berpendapat',
   'Dosen menciptakan suasana kelas yang aktif dan mendorong saya untuk bertanya dan berpendapat',
   '我营造活跃的课堂氛围，鼓励学生提问和发表意见',
   '教师营造活跃的课堂氛围，鼓励我提问和发表意见'),
  ('D6', 2,
   'Tingkat kehadiran dan partisipasi aktif mahasiswa dalam perkuliahan saya cukup tinggi',
   'Saya hadir dan berpartisipasi aktif dalam setiap sesi perkuliahan MK ini',
   '学生在我的课堂中出勤率和积极参与度较高',
   '我积极参加本课程的每一堂课'),
  ('D7', 3,
   'Saya memberikan kesempatan diskusi kelompok atau kolaborasi antar mahasiswa yang bermakna',
   'Ada kesempatan diskusi kelompok atau kerja sama yang bermakna dalam perkuliahan ini',
   '我为学生提供有意义的小组讨论或协作机会',
   '本课程中有有意义的小组讨论或合作机会')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items D.3 — Penilaian ─────────────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'D.3')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('D8', 1,
   'Saya memberikan tugas/kuis/ujian yang relevan dan mengukur ketercapaian CPL secara tepat',
   'Tugas, kuis, dan ujian dalam MK ini relevan dan mengukur pemahaman saya terhadap materi',
   '我布置的作业/测验/考试相关且能准确衡量学习成果的达成情况',
   '本课程的作业、测验和考试与教学内容相关，能衡量我对教材的理解'),
  ('D9', 2,
   'Saya memberikan umpan balik yang konstruktif dan tepat waktu atas hasil pekerjaan mahasiswa',
   'Dosen memberikan umpan balik yang konstruktif dan tepat waktu atas tugas dan ujian saya',
   '我及时向学生提供有建设性的反馈',
   '教师及时对我的作业和考试提供建设性的反馈'),
  ('D10', 3,
   'Sistem penilaian yang saya terapkan transparan, adil, dan telah dikomunikasikan sejak awal',
   'Sistem penilaian MK ini transparan, adil, dan sudah dijelaskan sejak awal perkuliahan',
   '我实施的评分体系透明、公平，并从一开始就进行了说明',
   '本课程的评分体系透明、公平，并在课程开始时就进行了说明')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items E.1 — Pencapaian Kompetensi ────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'E.1')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('E1', 1,
   'Mahasiswa yang mengikuti MK saya mampu mencapai CPL yang telah ditetapkan',
   'Setelah mengikuti MK ini, saya merasa mampu mencapai Capaian Pembelajaran (CPL) yang ditetapkan',
   '参加我课程的学生能够达到既定的学习成果',
   '学完本课程后，我感到能够达到既定的学习成果'),
  ('E2', 2,
   'Mahasiswa menunjukkan peningkatan kemampuan berkomunikasi dalam konteks budaya Tiongkok',
   'MK ini meningkatkan kemampuan saya untuk berkomunikasi dalam konteks budaya Tiongkok',
   '学生在中国文化语境下的沟通能力有所提升',
   '本课程提升了我在中国文化语境中的沟通能力'),
  ('E3', 3,
   'Nilai akhir mahasiswa mencerminkan ketercapaian kompetensi yang sesungguhnya',
   'Nilai akhir yang saya peroleh mencerminkan kemampuan dan usaha saya yang sesungguhnya',
   '学生的最终成绩真实反映了其能力达成情况',
   '我获得的最终成绩真实反映了我的能力和努力')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items E.2 — Pemahaman Budaya ──────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'E.2')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('E4', 1,
   'MK yang saya ampu berhasil meningkatkan pemahaman mahasiswa tentang budaya Tiongkok secara komprehensif',
   'MK ini meningkatkan pemahaman saya tentang budaya Tiongkok secara menyeluruh',
   '我所教的课程成功提升了学生对中国文化的全面理解',
   '本课程全面提升了我对中国文化的理解'),
  ('E5', 2,
   'Mahasiswa mampu menganalisis persamaan dan perbedaan antara budaya Tiongkok dan budaya lokal',
   'Saya mampu menganalisis persamaan dan perbedaan antara budaya Tiongkok dan budaya saya sendiri',
   '学生能够分析中国文化与本土文化之间的异同',
   '我能够分析中国文化与我自己文化之间的异同'),
  ('E6', 3,
   'MK ini mendorong mahasiswa untuk memiliki sikap toleran dan apresiatif terhadap budaya Tiongkok',
   'MK ini mendorong saya untuk lebih toleran dan apresiatif terhadap budaya Tiongkok',
   '本课程促进学生对中国文化持宽容和欣赏的态度',
   '本课程促使我对中国文化更加包容和欣赏')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Items E.3 — Kepuasan & Dampak ────────────────────────────────────────────
WITH sd AS (SELECT id FROM cipp_sub_dimensions WHERE kode = 'E.3')
INSERT INTO instrument_items (sub_dimension_id, kode, nomor_urut, text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa, is_active)
SELECT sd.id, kode, urut, td, tm, zd, zm, true FROM sd, (VALUES
  ('E7', 1,
   'Saya merasa puas dengan pelaksanaan MK Budaya Tiongkok yang saya ampu secara keseluruhan',
   'Saya merasa puas dengan pelaksanaan MK Budaya Tiongkok secara keseluruhan',
   '我对自己所教的中国文化课程的整体实施感到满意',
   '我对中国文化课程的整体实施感到满意'),
  ('E8', 2,
   'Pengetahuan dan pengalaman dari MK ini bermanfaat bagi pengembangan karir akademis mahasiswa',
   'Pengetahuan dari MK ini bermanfaat untuk pengembangan karir dan kehidupan saya',
   '本课程的知识和经验有利于学生的学术职业发展',
   '本课程的知识对我的职业发展和生活有所帮助'),
  ('E9', 3,
   'Jika diberi kesempatan, saya bersedia mengajar MK Budaya Tiongkok kembali dengan antusias',
   'Jika ada kesempatan, saya akan merekomendasikan MK ini kepada teman-teman saya',
   '如有机会，我愿意继续充满热情地教授中国文化课程',
   '如有机会，我会向朋友推荐这门课程')
) AS v(kode, urut, td, tm, zd, zm)
ON CONFLICT (kode) DO NOTHING;

-- ── Open Questions ────────────────────────────────────────────────────────────
INSERT INTO open_questions (kode, pertanyaan_id, pertanyaan_zh, tujuan, target_role, is_required, urutan, is_active)
VALUES
  ('OQ1',
   'Menurut Anda, apa kelebihan utama dari mata kuliah Budaya Tiongkok ini?',
   '您认为这门中国文化课程的主要优点是什么？',
   'Menggali persepsi positif responden', 'semua', false, 1, true),
  ('OQ2',
   'Apa saran Anda untuk meningkatkan kualitas mata kuliah Budaya Tiongkok ke depannya?',
   '您对提高中国文化课程质量有什么建议？',
   'Menggali masukan perbaikan', 'semua', false, 2, true),
  ('OQ3',
   'Apakah ada topik budaya Tiongkok yang belum dibahas namun menurut Anda penting untuk ditambahkan?',
   '是否有尚未讨论但您认为应该添加的中国文化话题？',
   'Identifikasi gap materi', 'semua', false, 3, true)
ON CONFLICT (kode) DO NOTHING;

COMMIT;

-- Verifikasi
SELECT 'Dimensions' AS tabel, COUNT(*) AS jumlah FROM cipp_dimensions
UNION ALL
SELECT 'Sub-Dimensions', COUNT(*) FROM cipp_sub_dimensions
UNION ALL
SELECT 'Items', COUNT(*) FROM instrument_items
UNION ALL
SELECT 'Open Questions', COUNT(*) FROM open_questions;
