"""
Seed data dari Excel:
- 10 universitas + program studi + mata kuliah contoh
- 59 instrument items (dosen + mahasiswa, ID + ZH)
- Update open questions dengan versi ZH
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy import select, delete
from app.database import AsyncSessionLocal
from app.models.academic import University, Program, Course
from app.models.instrument import CippSubDimension, InstrumentItem, OpenQuestion


UNIVERSITIES = [
    {"nama": "Universitas Al Azhar Indonesia", "nama_singkat": "UAI", "jenis": "swasta", "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta", "website": "https://uai.ac.id", "tahun_berdiri": 2004,
     "program": "Bahasa dan Kebudayaan Tiongkok", "program_singkat": "BKT"},
    {"nama": "Universitas Negeri Jakarta", "nama_singkat": "UNJ", "jenis": "negeri", "kota": "Jakarta Timur", "provinsi": "DKI Jakarta", "website": "https://fbs.unj.ac.id", "tahun_berdiri": 2006,
     "program": "Pendidikan Bahasa Mandarin", "program_singkat": "PBM"},
    {"nama": "Universitas Hasanuddin", "nama_singkat": "UNHAS", "jenis": "negeri", "kota": "Makassar", "provinsi": "Sulawesi Selatan", "website": "https://prodi.unhas.ac.id", "tahun_berdiri": 2018,
     "program": "Bahasa Mandarin dan Kebudayaan Tiongkok", "program_singkat": "BMKT"},
    {"nama": "Universitas Universal", "nama_singkat": "UVERS", "jenis": "swasta", "kota": "Batam", "provinsi": "Kepulauan Riau", "website": "https://fpbb.uvers.ac.id", "tahun_berdiri": 2013,
     "program": "Pendidikan Bahasa Mandarin", "program_singkat": "PBM"},
    {"nama": "Universitas Negeri Makassar", "nama_singkat": "UNM", "jenis": "negeri", "kota": "Makassar", "provinsi": "Sulawesi Selatan", "website": "http://pbm.fbs.unm.ac.id", "tahun_berdiri": 2015,
     "program": "Pendidikan Bahasa Mandarin", "program_singkat": "PBM"},
    {"nama": "Universitas Negeri Semarang", "nama_singkat": "UNNES", "jenis": "negeri", "kota": "Semarang", "provinsi": "Jawa Tengah", "website": "https://unnes.ac.id", "tahun_berdiri": 2011,
     "program": "Pendidikan Bahasa Mandarin", "program_singkat": "PBM"},
    {"nama": "Universitas Sumatera Utara", "nama_singkat": "USU", "jenis": "negeri", "kota": "Medan", "provinsi": "Sumatera Utara", "website": "https://fib.usu.ac.id", "tahun_berdiri": 2007,
     "program": "Bahasa Mandarin", "program_singkat": "BM"},
    {"nama": "Universitas Tanjungpura", "nama_singkat": "UNTAN", "jenis": "negeri", "kota": "Pontianak", "provinsi": "Kalimantan Barat", "website": None, "tahun_berdiri": None,
     "program": "Bahasa Mandarin", "program_singkat": "BM"},
    {"nama": "Universitas Indonesia", "nama_singkat": "UI", "jenis": "negeri", "kota": "Depok", "provinsi": "Jawa Barat", "website": "https://ui.ac.id", "tahun_berdiri": 1950,
     "program": "Sastra Cina", "program_singkat": "SC"},
    {"nama": "Universitas Sebelas Maret", "nama_singkat": "UNS", "jenis": "negeri", "kota": "Surakarta", "provinsi": "Jawa Tengah", "website": "https://uns.ac.id", "tahun_berdiri": None,
     "program": "Bahasa Mandarin dan Kebudayaan Tiongkok", "program_singkat": "BMKT"},
]

COURSES_TEMPLATE = [
    {"kode_mk": "BT001", "nama_id": "Kebudayaan Tiongkok", "nama_zh": "中国文化", "sks": 3, "semester": 3},
    {"kode_mk": "BT002", "nama_id": "Sejarah Tiongkok", "nama_zh": "中国历史", "sks": 2, "semester": 4},
    {"kode_mk": "BT003", "nama_id": "Filsafat Tiongkok", "nama_zh": "中国哲学", "sks": 2, "semester": 5},
]

ITEMS_DOSEN = [
    ("B.1","CD1.1",1,"Saya memahami kebutuhan mahasiswa terhadap pembelajaran Budaya Tiongkok melalui analisis yang sistematis","Analisis kebutuhan","Persepsi dosen terhadap konteks institusional"),
    ("B.1","CD1.2",2,"Tujuan kelas Budaya Tiongkok sejalan dengan kebutuhan lapangan kerja terkait Tiongkok","Relevansi pasar","Persepsi dosen terhadap konteks institusional"),
    ("B.1","CD1.3",3,"Saya menyadari pentingnya kursus ini dalam konteks hubungan Indonesia-Tiongkok","Kesadaran Contexttual","Persepsi dosen terhadap konteks institusional"),
    ("B.1","CD1.4",4,"Saya secara rutin memperbarui materi kelas berdasarkan perkembangan terbaru hubungan Indonesia-Tiongkok","Relevansi kontekstual","Persepsi dosen terhadap konteks institusional"),
    ("B.2","CD2.1",5,"Tujuan pembelajaran kelas Budaya Tiongkok yang saya ajarkan telah dirumuskan secara jelas dan terukur","Kejelasan tujuan","Kejelasan Tujuan Instruksional"),
    ("B.2","CD2.2",6,"Capaian pembelajaran kelas ini sesuai dengan standar kompetensi nasional (KKNI/SN-Dikti)","Standar kompetensi","Kejelasan Tujuan Instruksional"),
    ("B.2","CD2.3",7,"Saya memastikan setiap mahasiswa memahami tujuan pembelajaran di awal perkuliahan","Komunikasi tujuan","Kejelasan Tujuan Instruksional"),
    ("B.2","CD2.4",8,"Tujuan pembelajaran kelas ini mendukung pengembangan kompetensi lintas budaya mahasiswa","Kompetensi lintas budaya","Kejelasan Tujuan Instruksional"),
    ("B.3","CD3.1",9,"Institusi memiliki kebijakan yang mendukung pengembangan kelas Budaya Tiongkok","Dukungan kebijakan","Dukungan Kebijakan Institusi"),
    ("B.3","CD3.2",10,"Institusi menyediakan sumber daya yang memadai untuk pelaksanaan kelas ini (ruang, fasilitas, anggaran)","Ketersediaan sumber daya","Dukungan Kebijakan Institusi"),
    ("B.3","CD3.3",11,"Ada mekanisme evaluasi institusional yang teratur untuk kelas Budaya Tiongkok","Evaluasi institusional","Dukungan Kebijakan Institusi"),
    ("C.1","ID1.1",12,"Kurikulum kelas Budaya Tiongkok yang saya ajarkan sudah komprehensif dan up-to-date","Kelengkapan kurikulum","Kualitas Desain Kurikulum"),
    ("C.1","ID1.2",13,"Konten kelas mencakup aspek budaya Tiongkok yang relevan dan beragam","Cakupan konten","Kualitas Desain Kurikulum"),
    ("C.1","ID1.3",14,"Urutan materi dalam silabus disusun secara logis dan progresif","Sekuens materi","Kualitas Desain Kurikulum"),
    ("C.1","ID1.4",15,"Silabus kelas ini telah direviu oleh sejawat atau pakar budaya Tiongkok","Reviu sejawat","Kualitas Desain Kurikulum"),
    ("C.2","ID2.1",16,"Saya memiliki latar belakang akademik yang memadai untuk mengajar Budaya Tiongkok","Kualifikasi akademik","Kompetensi Pengajar"),
    ("C.2","ID2.2",17,"Saya secara aktif mengikuti pelatihan atau seminar terkait budaya dan pedagogi Tiongkok","Pengembangan profesional","Kompetensi Pengajar"),
    ("C.2","ID2.3",18,"Saya memiliki pengalaman langsung dengan budaya Tiongkok (kunjungan, kolaborasi, atau studi)","Pengalaman budaya","Kompetensi Pengajar"),
    ("C.2","ID2.4",19,"Kemampuan bahasa Mandarin saya mendukung penyampaian materi budaya secara autentik","Kemampuan bahasa","Kompetensi Pengajar"),
    ("C.3","ID3.1",20,"Buku teks dan referensi yang digunakan dalam kelas ini berkualitas tinggi dan relevan","Kualitas referensi","Ketersediaan Sumber Belajar"),
    ("C.3","ID3.2",21,"Perpustakaan atau institusi menyediakan sumber daya yang cukup untuk mendukung pembelajaran budaya Tiongkok","Sumber daya perpustakaan","Ketersediaan Sumber Belajar"),
    ("C.3","ID3.3",22,"Saya menggunakan media digital dan teknologi untuk memperkaya pengalaman belajar mahasiswa","Teknologi pembelajaran","Ketersediaan Sumber Belajar"),
    ("C.3","ID3.4",23,"Materi autentik dari Tiongkok (film, musik, teks asli) digunakan secara efektif dalam kelas","Materi autentik","Ketersediaan Sumber Belajar"),
    ("C.4","ID4.1",24,"Ada alokasi waktu yang cukup untuk setiap topik budaya dalam jadwal perkuliahan","Alokasi waktu","Kecukupan Waktu & Jadwal"),
    ("C.4","ID4.2",25,"Beban tugas dan penilaian dalam kelas ini proporsional dengan jumlah SKS","Beban kerja","Kecukupan Waktu & Jadwal"),
    ("C.4","ID4.3",26,"Jadwal perkuliahan memungkinkan diskusi mendalam tentang topik budaya yang kompleks","Kualitas diskusi","Kecukupan Waktu & Jadwal"),
    ("D.1","PD1.1",27,"Saya menggunakan berbagai metode pengajaran yang sesuai dengan materi budaya (ceramah, diskusi, simulasi, role-play)","Variasi metode","Implementasi Strategi Pengajaran"),
    ("D.1","PD1.2",28,"Saya mendorong mahasiswa untuk aktif berpartisipasi dalam diskusi kelas","Partisipasi aktif","Implementasi Strategi Pengajaran"),
    ("D.1","PD1.3",29,"Saya mengintegrasikan pendekatan komparatif (budaya Indonesia vs Tiongkok) dalam pengajaran","Pendekatan komparatif","Implementasi Strategi Pengajaran"),
    ("D.1","PD1.4",30,"Saya memanfaatkan teknologi digital untuk meningkatkan pengalaman belajar budaya mahasiswa","Integrasi teknologi","Implementasi Strategi Pengajaran"),
    ("D.2","PD2.1",31,"Saya memberikan umpan balik yang konstruktif dan tepat waktu terhadap tugas mahasiswa","Kualitas umpan balik","Interaksi Dosen-Mahasiswa"),
    ("D.2","PD2.2",32,"Saya menciptakan lingkungan belajar yang inklusif dan menghormati keberagaman perspektif","Lingkungan inklusif","Interaksi Dosen-Mahasiswa"),
    ("D.2","PD2.3",33,"Saya tersedia untuk konsultasi di luar jam kelas terkait materi budaya Tiongkok","Aksesibilitas dosen","Interaksi Dosen-Mahasiswa"),
    ("D.2","PD2.4",34,"Interaksi saya dengan mahasiswa mendorong pemikiran kritis tentang isu-isu budaya","Pemikiran kritis","Interaksi Dosen-Mahasiswa"),
    ("D.3","PD3.1",35,"Sistem penilaian yang saya gunakan secara adil mengukur pemahaman dan apresiasi budaya mahasiswa","Keadilan penilaian","Sistem Penilaian & Evaluasi"),
    ("D.3","PD3.2",36,"Saya menggunakan berbagai instrumen penilaian (ujian, presentasi, proyek, refleksi) dalam kelas ini","Keragaman instrumen","Sistem Penilaian & Evaluasi"),
    ("D.3","PD3.3",37,"Rubrik penilaian saya transparan dan dipahami dengan baik oleh mahasiswa","Transparansi rubrik","Sistem Penilaian & Evaluasi"),
    ("D.3","PD3.4",38,"Saya melakukan evaluasi formatif secara reguler untuk memantau kemajuan mahasiswa","Evaluasi formatif","Sistem Penilaian & Evaluasi"),
    ("D.4","PD4.1",39,"Keterlaksanaan kelas ini sesuai dengan rencana pembelajaran semester (RPS) yang telah disusun","Kesesuaian RPS","Keterlaksanaan Program"),
    ("D.4","PD4.2",40,"Hambatan dalam pelaksanaan kelas dapat diatasi dengan solusi yang efektif","Manajemen hambatan","Keterlaksanaan Program"),
    ("D.4","PD4.3",41,"Saya melakukan refleksi dan penyesuaian materi secara berkala berdasarkan respons mahasiswa","Refleksi pengajaran","Keterlaksanaan Program"),
    ("D.4","PD4.4",42,"Kolaborasi dengan dosen lain atau pakar budaya Tiongkok meningkatkan kualitas kelas ini","Kolaborasi sejawat","Keterlaksanaan Program"),
    ("E.1","RD1.1",43,"Mahasiswa dalam kelas saya menunjukkan peningkatan pemahaman tentang nilai-nilai budaya Tiongkok","Pemahaman budaya","Capaian Pembelajaran Mahasiswa"),
    ("E.1","RD1.2",44,"Mahasiswa mampu menganalisis fenomena budaya Tiongkok secara kritis setelah mengikuti kelas ini","Kemampuan analisis","Capaian Pembelajaran Mahasiswa"),
    ("E.1","RD1.3",45,"Mahasiswa dapat menghubungkan konsep budaya Tiongkok dengan konteks kehidupan nyata","Aplikasi pengetahuan","Capaian Pembelajaran Mahasiswa"),
    ("E.1","RD1.4",46,"Kompetensi lintas budaya mahasiswa meningkat secara signifikan setelah mengikuti kelas ini","Kompetensi lintas budaya","Capaian Pembelajaran Mahasiswa"),
    ("E.2","RD2.1",47,"Kelas Budaya Tiongkok yang saya ajarkan relevan dengan kebutuhan karier mahasiswa","Relevansi karier","Relevansi & Dampak Program"),
    ("E.2","RD2.2",48,"Program ini berkontribusi pada pengembangan sikap positif mahasiswa terhadap Tiongkok","Sikap positif","Relevansi & Dampak Program"),
    ("E.2","RD2.3",49,"Kelas ini mempersiapkan mahasiswa untuk berinteraksi secara efektif dalam konteks profesional Tiongkok","Kesiapan profesional","Relevansi & Dampak Program"),
    ("E.2","RD2.4",50,"Ada bukti dampak positif kelas ini pada kemampuan mahasiswa dalam situasi nyata lintas budaya","Dampak nyata","Relevansi & Dampak Program"),
    ("E.3","RD3.1",51,"Secara keseluruhan, kualitas kelas Budaya Tiongkok ini memenuhi standar akademik yang tinggi","Standar akademik","Kepuasan & Penilaian Keseluruhan"),
    ("E.3","RD3.2",52,"Saya puas dengan efektivitas pengajaran saya dalam kelas ini","Kepuasan mengajar","Kepuasan & Penilaian Keseluruhan"),
    ("E.3","RD3.3",53,"Kelas ini layak untuk dipertahankan dan dikembangkan lebih lanjut dalam kurikulum","Keberlanjutan program","Kepuasan & Penilaian Keseluruhan"),
    ("E.4","RD4.1",54,"Saya mendapat dukungan yang memadai dari institusi untuk terus meningkatkan kualitas kelas ini","Dukungan institusi","Pengembangan Berkelanjutan"),
    ("E.4","RD4.2",55,"Ada mekanisme umpan balik yang efektif antara mahasiswa, dosen, dan institusi untuk perbaikan kelas","Mekanisme umpan balik","Pengembangan Berkelanjutan"),
    ("E.4","RD4.3",56,"Hasil evaluasi kelas ini digunakan secara nyata untuk perbaikan kurikulum dan pengajaran","Tindak lanjut evaluasi","Pengembangan Berkelanjutan"),
    ("E.4","RD4.4",57,"Ada rencana pengembangan jangka panjang untuk kelas Budaya Tiongkok di institusi saya","Rencana pengembangan","Pengembangan Berkelanjutan"),
    ("E.4","RD4.5",58,"Kolaborasi dengan universitas atau lembaga Tiongkok direncanakan untuk meningkatkan kualitas program","Kolaborasi internasional","Pengembangan Berkelanjutan"),
]

ITEMS_MAHASISWA = [
    ("B.1","CD1.1","Saya merasa materi pembelajaran Budaya Tiongkok ini sangat sesuai dengan kebutuhan belajar saya."),
    ("B.1","CD1.2","Saya melihat kelas Budaya Tiongkok ini memiliki manfaat yang besar untuk peluang kerja saya di masa depan."),
    ("B.1","CD1.3","Saya memahami pentingnya mempelajari mata kuliah ini dalam konteks hubungan kerja sama Indonesia dan Tiongkok."),
    ("B.1","CD1.4","Saya merasa kebutuhan saya sebagai mahasiswa dipertimbangkan dalam penyusunan materi kelas ini."),
    ("B.2","CD2.1","Tujuan pembelajaran kelas ini dijelaskan secara jelas oleh dosen di awal perkuliahan."),
    ("B.2","CD2.2","Saya memahami apa yang diharapkan dari saya setelah menyelesaikan kelas ini."),
    ("B.2","CD2.3","Capaian pembelajaran kelas ini relevan dengan kompetensi yang saya butuhkan."),
    ("B.2","CD2.4","Tujuan pembelajaran kelas ini mendukung pengembangan kompetensi lintas budaya saya."),
    ("B.3","CD3.1","Institusi saya mendukung pengembangan kelas Budaya Tiongkok secara aktif."),
    ("B.3","CD3.2","Fasilitas yang tersedia (ruang kelas, perpustakaan, media) mendukung pembelajaran budaya Tiongkok."),
    ("B.3","CD3.3","Ada program atau kegiatan institusional yang mendukung pembelajaran budaya Tiongkok di luar kelas."),
    ("C.1","ID1.1","Kurikulum kelas Budaya Tiongkok yang saya ikuti komprehensif dan mencakup berbagai aspek budaya."),
    ("C.1","ID1.2","Materi yang diajarkan relevan dengan perkembangan terkini hubungan Indonesia-Tiongkok."),
    ("C.1","ID1.3","Urutan penyampaian materi dalam kelas ini logis dan mudah diikuti."),
    ("C.1","ID1.4","Konten kelas ini memberikan pemahaman yang seimbang tentang berbagai aspek budaya Tiongkok."),
    ("C.2","ID2.1","Dosen pengajar kelas ini memiliki pengetahuan yang luas tentang budaya Tiongkok."),
    ("C.2","ID2.2","Dosen mampu menyampaikan materi budaya Tiongkok dengan cara yang menarik dan mudah dipahami."),
    ("C.2","ID2.3","Dosen menggunakan pengalaman pribadi atau contoh nyata untuk menjelaskan konsep budaya."),
    ("C.2","ID2.4","Kemampuan bahasa Mandarin dosen mendukung pembelajaran budaya secara autentik."),
    ("C.3","ID3.1","Buku teks dan materi referensi yang digunakan dalam kelas ini berkualitas dan relevan."),
    ("C.3","ID3.2","Sumber belajar yang disediakan institusi (perpustakaan, database) memadai untuk mendukung studi budaya Tiongkok."),
    ("C.3","ID3.3","Penggunaan media digital dan teknologi dalam kelas ini meningkatkan pengalaman belajar saya."),
    ("C.3","ID3.4","Materi autentik dari Tiongkok (film, musik, teks) digunakan secara efektif untuk memperkaya pembelajaran."),
    ("C.4","ID4.1","Alokasi waktu untuk setiap topik budaya dalam kelas ini proporsional."),
    ("C.4","ID4.2","Beban tugas dan penilaian dalam kelas ini seimbang dengan jumlah SKS."),
    ("C.4","ID4.3","Jadwal perkuliahan memberikan waktu yang cukup untuk memahami topik budaya yang kompleks."),
    ("D.1","PD1.1","Metode pengajaran yang digunakan dalam kelas ini bervariasi dan menarik (ceramah, diskusi, role-play, dll.)."),
    ("D.1","PD1.2","Saya memiliki kesempatan yang cukup untuk berpartisipasi aktif dalam diskusi kelas."),
    ("D.1","PD1.3","Pendekatan komparatif (budaya Indonesia vs Tiongkok) digunakan secara efektif dalam pengajaran."),
    ("D.1","PD1.4","Penggunaan teknologi digital dalam kelas ini meningkatkan pemahaman saya tentang budaya Tiongkok."),
    ("D.2","PD2.1","Dosen memberikan umpan balik yang konstruktif dan membantu terhadap tugas dan pertanyaan saya."),
    ("D.2","PD2.2","Dosen menciptakan lingkungan belajar yang inklusif dan menghargai perspektif yang beragam."),
    ("D.2","PD2.3","Dosen mudah dihubungi untuk konsultasi di luar jam kelas."),
    ("D.2","PD2.4","Interaksi dengan dosen mendorong saya untuk berpikir kritis tentang isu-isu budaya."),
    ("D.3","PD3.1","Sistem penilaian dalam kelas ini adil dan mencerminkan pemahaman saya tentang budaya Tiongkok."),
    ("D.3","PD3.2","Berbagai metode penilaian (ujian, presentasi, proyek) digunakan dalam kelas ini."),
    ("D.3","PD3.3","Rubrik penilaian dijelaskan dengan transparan sehingga saya tahu apa yang diharapkan."),
    ("D.3","PD3.4","Evaluasi formatif (kuis, diskusi, tugas kecil) membantu saya memantau kemajuan belajar."),
    ("D.4","PD4.1","Pelaksanaan kelas ini sesuai dengan rencana pembelajaran yang telah disampaikan di awal semester."),
    ("D.4","PD4.2","Hambatan dalam perkuliahan (teknis, jadwal) ditangani dengan baik oleh dosen."),
    ("D.4","PD4.3","Dosen melakukan penyesuaian materi berdasarkan kebutuhan dan respons mahasiswa."),
    ("D.4","PD4.4","Adanya kolaborasi atau tamu ahli dalam kelas ini memperkaya pembelajaran budaya saya."),
    ("E.1","RD1.1","Pemahaman saya tentang nilai-nilai dan tradisi budaya Tiongkok meningkat setelah mengikuti kelas ini."),
    ("E.1","RD1.2","Saya mampu menganalisis fenomena budaya Tiongkok secara lebih kritis setelah kelas ini."),
    ("E.1","RD1.3","Saya dapat menghubungkan konsep budaya Tiongkok dengan situasi kehidupan nyata."),
    ("E.1","RD1.4","Kompetensi lintas budaya saya (memahami dan berinteraksi dengan budaya berbeda) meningkat."),
    ("E.2","RD2.1","Kelas Budaya Tiongkok ini relevan dengan bidang karier yang ingin saya tekuni."),
    ("E.2","RD2.2","Sikap saya terhadap budaya dan masyarakat Tiongkok menjadi lebih positif setelah kelas ini."),
    ("E.2","RD2.3","Kelas ini mempersiapkan saya untuk berinteraksi secara profesional dalam konteks bisnis atau akademik Tiongkok."),
    ("E.2","RD2.4","Pengetahuan budaya yang saya peroleh dari kelas ini bermanfaat dalam interaksi nyata lintas budaya."),
    ("E.3","RD3.1","Secara keseluruhan, kualitas kelas Budaya Tiongkok ini memenuhi ekspektasi akademik saya."),
    ("E.3","RD3.2","Saya puas dengan pengalaman belajar yang saya dapatkan dari kelas ini."),
    ("E.3","RD3.3","Saya akan merekomendasikan kelas ini kepada mahasiswa lain."),
    ("E.4","RD4.1","Institusi memberikan dukungan yang memadai untuk meningkatkan kualitas kelas Budaya Tiongkok."),
    ("E.4","RD4.2","Ada mekanisme yang jelas bagi mahasiswa untuk memberikan masukan demi perbaikan kelas."),
    ("E.4","RD4.3","Masukan mahasiswa benar-benar dipertimbangkan dalam perbaikan kelas di semester berikutnya."),
    ("E.4","RD4.4","Ada rencana pengembangan program Budaya Tiongkok yang lebih komprehensif di institusi saya."),
    ("E.4","RD4.5","Kesempatan untuk berinteraksi langsung dengan budaya Tiongkok (pertukaran, kunjungan) tersedia bagi mahasiswa."),
]

ITEMS_ZH_DOSEN = [
    "我通过系统性分析了解学生对中国文化课程的需求。", "汉语文化课程的目标与涉华就业市场需求相符。",
    "我意识到本课程在印中关系背景下的重要性。", "我定期根据印中关系最新动态更新课程内容。",
    "我所教授的中国文化课程的学习目标已明确且可衡量。", "本课程的学习成果符合国家能力标准（KKNI/SN-Dikti）。",
    "我确保每位学生在学期初了解学习目标。", "本课程的学习目标支持学生跨文化能力的发展。",
    "学校有支持中国文化课程发展的政策。", "学校提供充足的资源支持本课程的开展（教室、设施、经费）。",
    "学校有定期对中国文化课程进行机构评估的机制。",
    "我所教授的中国文化课程课程体系全面且与时俱进。", "课程内容涵盖多样且相关的中国文化方面。",
    "教学大纲中的材料顺序逻辑清晰、循序渐进。", "本课程教学大纲已经过同行或中国文化专家审阅。",
    "我具备教授中国文化所需的充分学术背景。", "我积极参与中国文化与教学法相关的培训或研讨会。",
    "我有直接接触中国文化的经历（访问、合作或学习）。", "我的汉语能力支持以真实方式讲授文化内容。",
    "本课程使用的教材和参考资料质量高且相关。", "图书馆或学校提供充足资源支持中国文化学习。",
    "我使用数字媒体和技术丰富学生的学习体验。", "来自中国的真实材料（电影、音乐、原文）在课堂中得到有效运用。",
    "课程表中每个文化主题都有充足的时间分配。", "本课程的作业和评估负担与学分数量相称。",
    "授课时间表允许对复杂文化主题进行深入讨论。",
    "我使用多种适合文化材料的教学方法（讲课、讨论、模拟、角色扮演）。",
    "我鼓励学生积极参与课堂讨论。", "我在教学中融入比较方法（印尼文化与中国文化对比）。",
    "我利用数字技术提升学生的文化学习体验。",
    "我对学生作业提供及时且有建设性的反馈。", "我营造包容性学习环境，尊重多元视角。",
    "我在课外为学生提供中国文化相关内容的咨询。", "我与学生的互动激发其对文化议题的批判性思考。",
    "我使用的评估系统公平衡量学生对文化的理解和欣赏。",
    "我在本课程中使用多种评估工具（考试、演讲、项目、反思）。",
    "我的评分标准透明，学生能充分理解。", "我定期进行形成性评估以监测学生进度。",
    "本课程的实施符合已制定的学期学习计划（RPS）。",
    "课程实施中的障碍能通过有效方案加以解决。",
    "我根据学生反馈定期反思和调整教学内容。",
    "与其他教师或中国文化专家的合作提升了本课程的质量。",
    "我班的学生表现出对中国文化价值观理解的提升。", "学生在本课程后能批判性地分析中国文化现象。",
    "学生能将中国文化概念与现实生活情境相联系。",
    "学生的跨文化能力在参加本课程后显著提升。",
    "我所教授的中国文化课程与学生的职业需求相关。",
    "该课程有助于培养学生对中国的积极态度。",
    "本课程使学生能在中国专业背景下有效互动。",
    "有证据表明本课程对学生在现实跨文化情境中的能力产生积极影响。",
    "总体而言，本中国文化课程的质量达到较高学术标准。", "我对自己在本课程中的教学效果感到满意。",
    "本课程值得在课程体系中保留并进一步发展。",
    "学校为我持续提升本课程质量提供了充足的支持。",
    "学生、教师与学校之间有有效的反馈机制用于课程改进。",
    "本课程的评估结果被切实用于课程与教学的改进。",
    "我所在学校有中国文化课程长期发展规划。",
    "计划与中国大学或机构开展合作以提升项目质量。",
]

ITEMS_ZH_MAHASISWA = [
    "我觉得中国文化课程的教学内容非常符合我的学习需求。",
    "我认为这门中国文化课程对我未来的就业机会有很大帮助。",
    "我理解在印中合作关系背景下学习这门课程的重要性。",
    "我感到在编写课程材料时考虑了我作为学生的需求。",
    "本课程的学习目标在学期初由教师清晰说明。",
    "我了解完成本课程后对我的期望。",
    "本课程的学习成果与我所需的能力相关。",
    "本课程的学习目标支持我跨文化能力的发展。",
    "我所在学校积极支持中国文化课程的发展。",
    "现有设施（教室、图书馆、媒体）支持中国文化的学习。",
    "有学校课外活动或项目支持课外中国文化学习。",
    "我所参加的中国文化课程课程体系全面，涵盖文化各方面。",
    "所教内容与印中关系最新动态相关。",
    "本课程的教学材料顺序逻辑清晰，易于跟进。",
    "课程内容对中国文化各方面的介绍均衡。",
    "本课程的授课教师对中国文化有广泛的了解。",
    "教师能以生动易懂的方式讲授中国文化内容。",
    "教师用个人经历或实际例子讲解文化概念。",
    "教师的汉语能力支持文化的真实学习。",
    "本课程使用的教材和参考资料质量高且相关。",
    "学校提供的学习资源（图书馆、数据库）足以支持中国文化研究。",
    "课堂中数字媒体和技术的使用提升了我的学习体验。",
    "来自中国的真实材料（电影、音乐、文本）被有效运用以丰富学习。",
    "本课程每个文化主题的时间分配合理。",
    "本课程的作业和评估负担与学分数量相称。",
    "授课时间表为理解复杂文化主题提供了充足时间。",
    "本课程使用的教学方法多样且有趣（讲课、讨论、角色扮演等）。",
    "我有足够的机会积极参与课堂讨论。",
    "比较方法（印尼文化与中国文化对比）在教学中得到有效运用。",
    "课堂中数字技术的运用加深了我对中国文化的理解。",
    "教师对我的作业和问题给予有建设性且有帮助的反馈。",
    "教师营造包容性学习环境，尊重多元视角。",
    "教师在课外容易联系以进行咨询。",
    "与教师的互动鼓励我批判性地思考文化议题。",
    "本课程的评估系统公平反映我对中国文化的理解。",
    "本课程使用多种评估方式（考试、演讲、项目）。",
    "评分标准透明说明，我知道评估期望。",
    "形成性评估（小测、讨论、小作业）帮助我监测学习进度。",
    "本课程的实施符合学期初告知的学习计划。",
    "课程中的障碍（技术、时间安排）由教师妥善处理。",
    "教师根据学生需求和反馈调整教学内容。",
    "课堂中的合作或特邀专家丰富了我的文化学习。",
    "参加本课程后，我对中国文化价值观和传统的理解有所提升。",
    "本课程后，我能更批判性地分析中国文化现象。",
    "我能将中国文化概念与现实生活情境相联系。",
    "我的跨文化能力（理解不同文化并与其互动）有所提升。",
    "这门中国文化课程与我想从事的职业方向相关。",
    "本课程后，我对中国文化和社会的态度变得更加积极。",
    "本课程使我能在中国商业或学术背景下专业互动。",
    "本课程获得的文化知识在实际跨文化互动中有益。",
    "总体而言，这门中国文化课程的质量达到了我的学术期望。",
    "我对本课程的学习体验感到满意。",
    "我会向其他同学推荐本课程。",
    "学校为提升中国文化课程质量提供了充足支持。",
    "有明确机制供学生提供课程改进意见。",
    "学生的意见在下学期课程改进中确实得到考虑。",
    "我所在学校有更全面的中国文化项目发展计划。",
    "学生有直接接触中国文化的机会（交流、访问）。",
]


async def seed_universities(db):
    result = await db.execute(select(University))
    if result.scalars().first():
        print("[skip] Universitas sudah ada")
        return

    for u in UNIVERSITIES:
        univ = University(
            nama=u["nama"].strip(),
            nama_singkat=u["nama_singkat"],
            jenis=u["jenis"],
            kota=u["kota"],
            provinsi=u["provinsi"],
            website=u.get("website"),
            tahun_berdiri=u.get("tahun_berdiri"),
            is_active=True,
        )
        db.add(univ)
        await db.flush()

        prog = Program(
            university_id=univ.id,
            nama=u["program"],
            nama_singkat=u["program_singkat"],
            jenjang="S1",
            tahun_berdiri=u.get("tahun_berdiri"),
            is_active=True,
        )
        db.add(prog)
        await db.flush()

        for c in COURSES_TEMPLATE:
            course = Course(
                program_id=prog.id,
                kode_mk=c["kode_mk"],
                nama_id=c["nama_id"],
                nama_zh=c["nama_zh"],
                sks=c["sks"],
                semester=c["semester"],
                is_active=True,
            )
            db.add(course)

    await db.commit()
    print(f"[seed] {len(UNIVERSITIES)} universitas + program studi + mata kuliah seeded.")


async def seed_instrument_items(db):
    result = await db.execute(select(InstrumentItem))
    if result.scalars().first():
        print("[skip] Instrument items sudah ada")
        return

    mhs_map = {row[1]: row[2] for row in ITEMS_MAHASISWA}
    zh_dosen_map = {row[1]: ITEMS_ZH_DOSEN[i] for i, row in enumerate(ITEMS_DOSEN)}
    zh_mhs_map = {row[1]: ITEMS_ZH_MAHASISWA[i] for i, row in enumerate(ITEMS_MAHASISWA)}

    subdim_map = {}
    result = await db.execute(select(CippSubDimension))
    for sd in result.scalars().all():
        subdim_map[sd.kode] = sd.id

    count = 0
    for i, (subdim_kode, kode, urutan, text_dosen, indikator, kompetensi) in enumerate(ITEMS_DOSEN):
        if subdim_kode not in subdim_map:
            print(f"[warn] Sub-dimensi {subdim_kode} tidak ditemukan, skip {kode}")
            continue

        item = InstrumentItem(
            sub_dimension_id=subdim_map[subdim_kode],
            kode=kode,
            nomor_urut=urutan,
            text_id_dosen=text_dosen,
            text_id_mahasiswa=mhs_map.get(kode, text_dosen),
            text_zh_dosen=zh_dosen_map.get(kode, ""),
            text_zh_mahasiswa=zh_mhs_map.get(kode, ""),
            indikator=indikator,
            kompetensi_dosen=kompetensi,
            kompetensi_mahasiswa=None,
        )
        db.add(item)
        count += 1

    await db.commit()
    print(f"[seed] {count} instrument items seeded.")


async def update_open_questions_zh(db):
    ZH_MAP = {
        "F1": "您认为您所参加的中国文化课程有哪些主要优点？",
        "F2": "该课程有哪些不足之处或需要改进的地方？",
        "F3": "您认为哪种评估或测试方法最能有效衡量对文化的理解？",
        "F4": "您希望提议哪些额外的主题或活动来提升课程质量？",
        "F5": "参加本课程期间，您最难忘的学习经历是什么？",
        "F6": "参加本课程后，您对中国的态度或看法是否有所改变？请说明。",
        "F7": "本问卷中尚未涵盖但对评估重要的方面或指标有哪些？",
        "F8": "从教学者角度对改进本问卷的建议：",
    }
    result = await db.execute(select(OpenQuestion))
    updated = 0
    for oq in result.scalars().all():
        if oq.kode in ZH_MAP and oq.pertanyaan_zh != ZH_MAP[oq.kode]:
            oq.pertanyaan_zh = ZH_MAP[oq.kode]
            updated += 1
    await db.commit()
    if updated:
        print(f"[seed] {updated} open questions ZH updated.")


async def main():
    async with AsyncSessionLocal() as db:
        await seed_universities(db)
        await seed_instrument_items(db)
        await update_open_questions_zh(db)
    print("Seed selesai!")

asyncio.run(main())
