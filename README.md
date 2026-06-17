# Write Thai Academic Book

`write-thai-academic-book` เป็น skill สำหรับช่วยวางแผน ร่าง ตรวจ แก้ไข และผลิตต้นฉบับงานวิชาการภาษาไทย โดยออกแบบให้เหมาะกับงาน 3 ประเภท ได้แก่

1. `teaching-notes` — เอกสารคำสอน เป้าหมายคุณภาพภายในระดับ A-equivalent
2. `book` — หนังสือ เป้าหมายระดับ A
3. `textbook` — ตำรา เป้าหมายระดับ A

ระบบนี้เน้นการทำงานแบบเป็นขั้นตอน ใช้ไฟล์งานเดิมเป็นแหล่งอ้างอิงหลัก แยกผลลัพธ์รายบท และหยุดรอการอนุมัติจากผู้ใช้ก่อนเริ่มขั้นถัดไป เพื่อลดปัญหาการร่างผิดลำดับ การสร้างข้อมูลซ้ำ การตีความประเภทเอกสารผิด และการเขียนทับต้นฉบับเดิมโดยไม่ตั้งใจ

---

## สารบัญ

- [ภาพรวมการทำงาน](#ภาพรวมการทำงาน)
- [เหมาะกับใคร](#เหมาะกับใคร)
- [หลักการสำคัญ](#หลักการสำคัญ)
- [โครงสร้าง repository](#โครงสร้าง-repository)
- [การติดตั้ง](#การติดตั้ง)
- [การตรวจสอบหลังติดตั้ง](#การตรวจสอบหลังติดตั้ง)
- [แนวคิดเรื่อง project-id และ output](#แนวคิดเรื่อง-project-id-และ-output)
- [ประเภทเอกสารที่รองรับ](#ประเภทเอกสารที่รองรับ)
- [สถานะการอนุมัติ](#สถานะการอนุมัติ)
- [Workflow หลัก](#workflow-หลัก)
- [Workflow A: เริ่มเขียนงานใหม่ตั้งแต่ต้น](#workflow-a-เริ่มเขียนงานใหม่ตั้งแต่ต้น)
- [Workflow B: มีต้นฉบับ DOCX เดิมทั้งเล่ม](#workflow-b-มีต้นฉบับ-docx-เดิมทั้งเล่ม)
- [Workflow C: มีร่างเฉพาะบท](#workflow-c-มีร่างเฉพาะบท)
- [คำสั่ง task ทั้งหมด](#คำสั่ง-task-ทั้งหมด)
- [โครงสร้างผลลัพธ์](#โครงสร้างผลลัพธ์)
- [การใช้ไฟล์เกณฑ์หรือคู่มือของหน่วยงาน](#การใช้ไฟล์เกณฑ์หรือคู่มือของหน่วยงาน)
- [ตัวอย่าง prompt ใช้งานจริง](#ตัวอย่าง-prompt-ใช้งานจริง)
- [ข้อควรระวัง](#ข้อควรระวัง)
- [การแก้ปัญหาที่พบบ่อย](#การแก้ปัญหาที่พบบ่อย)
- [หมายเหตุสำหรับผู้พัฒนา](#หมายเหตุสำหรับผู้พัฒนา)
- [License](#license)

---

## ภาพรวมการทำงาน

skill นี้ไม่ได้เป็นเพียง prompt สำหรับเขียนหนังสือ แต่เป็นระบบ workflow สำหรับจัดการต้นฉบับวิชาการทั้งโครงการ โดยแบ่งงานออกเป็น task ย่อย เช่น เลือกประเภทเอกสาร สร้างข้อมูลโครงการ ร่างโครงร่าง ตรวจโครงร่าง ร่างบท ตรวจบท แก้บท ตรวจทั้งเล่ม และผลิตไฟล์สุดท้าย

หลักการสำคัญคือ **หนึ่งคำสั่งทำเพียงหนึ่ง task** เมื่อ task เสร็จ ระบบจะสร้าง artifact เฉพาะส่วนที่เกี่ยวข้อง ตั้งสถานะเป็น `PENDING` และหยุดรอให้ผู้ใช้ตรวจและอนุมัติก่อนเดินหน้าต่อ

ระบบจึงเหมาะกับงานที่ต้องการควบคุมคุณภาพเป็นลำดับ เช่น การจัดทำเอกสารคำสอน หนังสือ หรือตำราสำหรับการประเมินผลงานทางวิชาการ

---

## เหมาะกับใคร

เหมาะสำหรับ

- อาจารย์มหาวิทยาลัยที่ต้องการจัดทำเอกสารคำสอน หนังสือ หรือตำรา
- ผู้ที่มีต้นฉบับ DOCX อยู่แล้วและต้องการตรวจช่องว่างตามเกณฑ์คุณภาพ
- ผู้ที่ต้องการทำงานทีละบทโดยมีระบบ QC และบันทึกการแก้ไข
- ทีมที่ต้องการ workflow แบบมีหลักฐาน ตรวจสอบย้อนกลับได้ และไม่เขียนทับต้นฉบับเดิม

ไม่เหมาะสำหรับ

- การสั่งให้ AI เขียนทั้งเล่มในครั้งเดียว
- การผลิตเอกสารที่ไม่ต้องตรวจเกณฑ์หรือไม่ต้องมี approval gate
- การอ้างอิงเกณฑ์เฉพาะของสถาบันโดยไม่มีคู่มือหรือเอกสารจริงให้ตรวจ

---

## หลักการสำคัญ

1. **ทำทีละ task**  
   ห้ามรวมการร่าง ตรวจ แก้ และผลิตไฟล์สุดท้ายไว้ในคำสั่งเดียว

2. **ต้องเลือกประเภทเอกสารก่อนเสมอ**  
   ทุก project ต้องเริ่มจาก `select-document-type` และเลือกได้เพียง 1 ประเภท ได้แก่ `teaching-notes`, `book` หรือ `textbook`

3. **ใช้ artifact เดิมเป็นแหล่งข้อมูลหลัก**  
   ก่อนทำงาน ระบบต้องตรวจไฟล์ใน `output/<project-id>/` ก่อน ไม่เริ่มสร้างใหม่หากมีข้อมูลเดิมอยู่แล้ว

4. **ต้องมี human approval gate**  
   ผล `PASS`, `CONDITIONAL PASS` หรือ `MEETS_TARGET` จากเครื่องไม่ถือเป็นการอนุมัติของมนุษย์ ผู้ใช้ต้องตอบอนุมัติเอง เช่น `อนุมัติ`, `ผ่าน`, `โอเค`, `ไปต่อ` หรือ `แก้ตาม QC`

5. **ไม่เขียนทับต้นฉบับเดิม**  
   หากนำเข้า DOCX ระบบจะเก็บไฟล์ต้นฉบับไว้ที่ `source/original-manuscript.docx` แบบ byte-for-byte และสร้างไฟล์ผลลัพธ์ใหม่แยกต่างหาก

6. **ไม่สร้างหลักฐานเทียม**  
   ระบบต้องไม่แต่ง citation, ประสบการณ์ผู้เขียน, หลักฐานการสอน, สิทธิ์ภาพ, ผลวิจัย หรือคุณภาพระดับ A ขึ้นเอง หากไม่มีข้อมูลต้องระบุเป็น blocker

---

## โครงสร้าง repository

```text
book_drafter/
├── README.md
├── scripts/
│   ├── install.ps1
│   └── install.sh
├── packages/
│   └── write-thai-academic-book.zip
├── plugins/
│   └── write-thai-academic-book/
│       └── skills/
│           └── write-thai-academic-book/
│               ├── SKILL.md
│               ├── agents/
│               ├── assets/
│               ├── references/
│               └── scripts/
├── .agents/
└── .claude-plugin/
```

ส่วนที่สำคัญที่สุดคือ

- `plugins/write-thai-academic-book/skills/write-thai-academic-book/SKILL.md` — กติกาหลักของ skill
- `assets/` — template สำหรับ profile, approval, outline, QC, chapter, sources and rights และรายงานต่าง ๆ
- `references/` — เกณฑ์สรุปสำหรับประเภทเอกสาร คุณภาพ การบรรณาธิการ และ QC
- `scripts/check_task_gate.py` — ตรวจว่า task ที่เรียกสามารถทำต่อได้หรือไม่
- `scripts/import_manuscript.py` — นำเข้า DOCX โดยเก็บต้นฉบับและแยกบท
- `scripts/preflight.py` — ตรวจโครงสร้างเบื้องต้นก่อน QC เชิงวิชาการ
- `packages/write-thai-academic-book.zip` — package สำหรับนำเข้าโดยตรงในบางแพลตฟอร์ม

---

## การติดตั้ง

### สิ่งที่ควรมีก่อนติดตั้ง

ควรมีเครื่องมือพื้นฐานดังนี้

- Git
- Python 3 หากต้องใช้ script ตรวจ gate, import manuscript หรือ preflight
- PowerShell สำหรับ Windows หรือ shell สำหรับ macOS/Linux
- แพลตฟอร์มที่รองรับ skill เช่น Codex, Claude Cowork, Claude Code หรือ Google Antigravity

---

### วิธีที่ 1: ติดตั้งใน Codex ด้วย skill installer

ใน Codex ให้สั่งติดตั้งจาก repository นี้

```text
https://github.com/rijjina/book_drafter
```

เมื่อติดตั้งสำเร็จ skill จะอยู่ที่

```text
~/.agents/skills/write-thai-academic-book
```

---

### วิธีที่ 2: ติดตั้ง Codex บน Windows ด้วย PowerShell

```powershell
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
.\scripts\install.ps1 -Target codex
```

ตำแหน่งติดตั้งเริ่มต้นคือ

```text
$HOME\.agents\skills\write-thai-academic-book
```

---

### วิธีที่ 3: ติดตั้ง Google Antigravity บน Windows

```powershell
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
.\scripts\install.ps1 -Target antigravity
```

สำหรับ Antigravity CLI ใช้

```powershell
.\scripts\install.ps1 -Target antigravity-cli
```

ตำแหน่งติดตั้งเริ่มต้นของ Antigravity CLI คือ

```text
$HOME\.gemini\antigravity-cli\skills\write-thai-academic-book
```

---

### วิธีที่ 4: ติดตั้ง Claude Code บน Windows

```powershell
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
.\scripts\install.ps1 -Target claude-code
```

ตำแหน่งติดตั้งเริ่มต้นคือ

```text
$HOME\.claude\skills\write-thai-academic-book
```

---

### วิธีที่ 5: ติดตั้งบน macOS หรือ Linux

```bash
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
./scripts/install.sh codex
```

เปลี่ยน argument ท้ายคำสั่งได้ตามระบบที่ใช้

```bash
./scripts/install.sh codex
./scripts/install.sh antigravity
./scripts/install.sh antigravity-cli
./scripts/install.sh claude-code
```

---

### วิธีที่ 6: ติดตั้งใน Claude Cowork แบบ marketplace

1. เปิด `Customize > Plugins`
2. เลือก `Add marketplace > Add from a repository`
3. ใส่ URL

```text
https://github.com/rijjina/book_drafter
```

4. เลือกติดตั้ง `write-thai-academic-book` จาก marketplace ชื่อ `thai-academic-writing`

---

### วิธีที่ 7: นำเข้าเป็น skill โดยตรง

ดาวน์โหลดไฟล์

```text
packages/write-thai-academic-book.zip
```

แล้วนำเข้าในเมนู `Customize > Skills` ของแพลตฟอร์มที่รองรับ

---

## การตรวจสอบหลังติดตั้ง

หลังติดตั้ง ให้ตรวจว่ามีโฟลเดอร์ต่อไปนี้อยู่ในตำแหน่ง skill ของแพลตฟอร์ม

```text
write-thai-academic-book/
├── SKILL.md
├── assets/
├── references/
└── scripts/
```

จากนั้นลองเรียกใช้ด้วย prompt สั้น ๆ เช่น

```text
ใช้ skill write-thai-academic-book
อธิบาย task ที่รองรับแบบสั้น ๆ
```

หากระบบอ่าน skill ได้ ควรอธิบาย workflow ที่เริ่มจาก `select-document-type` และย้ำว่าต้องทำทีละ task

---

## แนวคิดเรื่อง project-id และ output

ทุกงานควรมี `project-id` เฉพาะ เช่น

```text
project-id: env-microbiology-book
project-id: algae-textbook-2026
project-id: teaching-notes-215312
```

คำแนะนำในการตั้งชื่อ

- ใช้ภาษาอังกฤษ ตัวเลข และขีดกลาง
- หลีกเลี่ยงเว้นวรรค
- ไม่ควรใช้ชื่อกว้างเกินไป เช่น `book` หรือ `draft`
- หากเปลี่ยนประเภทเอกสาร ควรสร้าง project-id ใหม่ เพื่อไม่ให้ artifact ปะปนกัน

ผลลัพธ์ทั้งหมดจะอยู่ภายใต้

```text
output/<project-id>/
```

---

## ประเภทเอกสารที่รองรับ

| ประเภทเอกสาร | ค่าในคำสั่ง | เป้าหมายคุณภาพ | ต้องเชื่อมรายวิชา | เหมาะกับ |
|---|---|---|---|---|
| เอกสารคำสอน | `teaching-notes` | A-equivalent ภายใน | ต้องเชื่อม | เอกสารประกอบการสอนที่ใช้กับรายวิชาชัดเจน |
| หนังสือ | `book` | A | ไม่บังคับ | งานวิชาการที่มีขอบเขตศาสตร์ ผู้อ่าน และคุณูปการทางวิชาการ |
| ตำรา | `textbook` | A | ต้องเชื่อม | ตำราที่สัมพันธ์กับรายวิชาหรือส่วนหนึ่งของรายวิชา |

### ข้อแตกต่างสำคัญ

#### `book`

หนังสือไม่บังคับให้มี มคอ.3, course code, CLO/PLO, จำนวนชั่วโมงสอน หรือหลักฐานการใช้ในชั้นเรียน แต่ต้องระบุ

- ขอบเขตทางวิชาการ
- กลุ่มผู้อ่าน
- แนวคิดแกนกลาง
- คุณูปการหรือมุมมองเชิงวิชาการของผู้เขียน
- ความทันสมัย ความลึก และการใช้ประโยชน์ในวงกว้าง

#### `textbook`

ตำราต้องสัมพันธ์กับรายวิชาหรือส่วนหนึ่งของรายวิชา โดยควรมี

- รหัส/ชื่อรายวิชา
- ขอบเขตเนื้อหาที่รับผิดชอบสอน
- ความเชื่อมโยงกับผลลัพธ์การเรียนรู้หรือวัตถุประสงค์รายวิชา หากหน่วยงานกำหนด
- โครงสร้างเนื้อหาที่เอื้อต่อการเรียนรู้

#### `teaching-notes`

เอกสารคำสอนต้องสัมพันธ์กับรายวิชาและการใช้สอนจริง โดยควรมี

- รายวิชาที่ใช้สอน
- ขอบเขตที่ผู้เขียนรับผิดชอบ
- ผลลัพธ์หรือวัตถุประสงค์การเรียนรู้
- กิจกรรมหรือคำถามท้ายบท
- หลักฐานการใช้หรือความเหมาะสมตามเกณฑ์ของหน่วยงาน

---

## สถานะการอนุมัติ

ระบบใช้ไฟล์ `approval.md` หลายระดับเพื่อควบคุม workflow

| สถานะ | ความหมาย |
|---|---|
| `PENDING` | task เสร็จแล้ว รอผู้ใช้ตรวจ |
| `APPROVED` | ผู้ใช้อนุมัติ task นั้นแล้ว |
| `CHANGES_REQUESTED` | ผู้ใช้ขอให้แก้ตาม QC หรือขอเปลี่ยนแปลง |
| `BLOCKED` | มีเงื่อนไขที่ทำต่อไม่ได้ |

คำตอบที่ใช้อนุมัติได้ เช่น

```text
อนุมัติ
ผ่าน
โอเค
ไปต่อ
```

คำตอบที่ใช้เปิดทางให้แก้ตาม QC เช่น

```text
แก้ตาม QC
ขอแก้ตามรายการ QC
ปรับตามข้อเสนอแนะ
```

ข้อสำคัญ: การอนุมัติหนึ่ง task ไม่ได้แปลว่าอนุมัติ task อื่นหรือบทอื่นด้วย

---

## Workflow หลัก

มี 3 เส้นทางหลัก

```text
A. เริ่มเขียนใหม่ตั้งแต่ต้น
select-document-type
→ project-setup
→ draft-outline
→ outline-qc
→ draft-chapter
→ chapter-qc
→ revise-chapter ถ้าจำเป็น
→ final-qc
→ produce-document
```

```text
B. มีต้นฉบับ DOCX เดิมทั้งเล่ม
select-document-type
→ import-manuscript
→ manuscript-qc
→ revise-manuscript ถ้าจำเป็น
→ final-qc
→ produce-document
```

```text
C. มีร่างเฉพาะบท
select-document-type
→ project-setup
→ draft-outline
→ outline-qc
→ draft-chapter <NN> พร้อม input
→ chapter-qc <NN>
→ revise-chapter <NN> ถ้าจำเป็น
→ final-qc
→ produce-document
```

---

## Workflow A: เริ่มเขียนงานใหม่ตั้งแต่ต้น

### ขั้นที่ 1: เลือกประเภทเอกสาร

```text
ใช้ skill write-thai-academic-book

task: select-document-type
project-id: env-microbiology-book
document-type: book
```

ระบบควรสร้าง

```text
output/env-microbiology-book/project/manuscript-profile.md
output/env-microbiology-book/project/type-approval.md
```

แล้วหยุดที่สถานะ `PENDING`

ให้ตรวจผล แล้วตอบ

```text
อนุมัติประเภทเอกสาร
```

---

### ขั้นที่ 2: ตั้งค่าโครงการ

```text
ใช้ skill write-thai-academic-book

task: project-setup
project-id: env-microbiology-book
หัวข้อ: การประยุกต์ใช้จุลินทรีย์เพื่อฟื้นฟูสิ่งแวดล้อม
กลุ่มผู้อ่าน: นักศึกษาระดับปริญญาตรีตอนปลาย บัณฑิตศึกษา และนักวิชาการสิ่งแวดล้อม
ขอบเขต: จุลินทรีย์กับการบำบัด ฟื้นฟู และจัดการสิ่งแวดล้อมระดับชุมชนถึงอุตสาหกรรม
หลักฐานและแหล่งข้อมูลที่มี: บทความวิจัยของผู้เขียน เอกสารสอนเดิม บทความ review และคู่มือหน่วยงาน
```

ระบบควรสร้าง

```text
project/project-brief.md
project/governing-standard.md
project/approval.md
```

ให้ตรวจผล แล้วตอบ

```text
อนุมัติโครงการ
```

---

### ขั้นที่ 3: ร่างโครงร่าง

```text
ใช้ skill write-thai-academic-book

task: draft-outline
project-id: env-microbiology-book
```

ระบบควรสร้าง

```text
project/outline.md
project/approval.md
```

ให้ตรวจโครงร่าง หากพอใจให้ตอบ

```text
อนุมัติโครงร่าง
```

---

### ขั้นที่ 4: ตรวจ QC โครงร่าง

```text
ใช้ skill write-thai-academic-book

task: outline-qc
project-id: env-microbiology-book
```

ระบบควรสร้าง

```text
project/outline-qc.md
project/approval.md
```

หาก QC ผ่านและไม่ต้องแก้ ให้ตอบ

```text
อนุมัติ QC โครงร่าง
```

หาก QC เสนอให้แก้ ให้ตอบ

```text
แก้ตาม QC
```

แล้วเรียก task แก้โครงร่าง

```text
ใช้ skill write-thai-academic-book

task: revise-outline
project-id: env-microbiology-book
```

---

### ขั้นที่ 5: ร่างบทที่ 1

```text
ใช้ skill write-thai-academic-book

task: draft-chapter 01
project-id: env-microbiology-book
```

ระบบควรสร้าง

```text
chapters/chapter-01/draft.md
chapters/chapter-01/sources-and-rights.md
chapters/chapter-01/approval.md
```

เมื่ออ่านแล้วพอใจ ให้ตอบ

```text
อนุมัติบทที่ 1
```

---

### ขั้นที่ 6: ตรวจ QC บทที่ 1

```text
ใช้ skill write-thai-academic-book

task: chapter-qc 01
project-id: env-microbiology-book
```

ระบบควรสร้าง

```text
chapters/chapter-01/chapter-qc.md
chapters/chapter-01/approval.md
```

หากต้องแก้ ให้ตอบ

```text
แก้ตาม QC
```

แล้วเรียก

```text
ใช้ skill write-thai-academic-book

task: revise-chapter 01
project-id: env-microbiology-book
```

เมื่อแก้เสร็จและอนุมัติแล้ว จึงเริ่มบทถัดไปได้

```text
ใช้ skill write-thai-academic-book

task: draft-chapter 02
project-id: env-microbiology-book
```

---

### ขั้นที่ 7: ตรวจทั้งเล่ม

เมื่อทุกบทผ่านกระบวนการและได้รับอนุมัติแล้ว ให้เรียก

```text
ใช้ skill write-thai-academic-book

task: final-qc
project-id: env-microbiology-book
chapter-count: 8
```

ระบบควรสร้าง

```text
final/preflight-report.md
final/final-qc.md
final/approval.md
```

หากผล final QC เป็น `MEETS_TARGET` และไม่มี blocker ให้ตอบ

```text
อนุมัติ final QC
```

---

### ขั้นที่ 8: ผลิต DOCX/PDF

```text
ใช้ skill write-thai-academic-book

task: produce-document
project-id: env-microbiology-book
chapter-count: 8
```

ระบบควรสร้าง

```text
final/manuscript.docx
final/manuscript.pdf
final/preflight-report.md
final/rendered/
final/approval.md
```

---

## Workflow B: มีต้นฉบับ DOCX เดิมทั้งเล่ม

ใช้ workflow นี้เมื่อมีไฟล์ต้นฉบับ เช่น

```text
D:\งาน\ต้นฉบับหนังสือ.docx
```

### ขั้นที่ 1: เลือกประเภทเอกสาร

```text
ใช้ skill write-thai-academic-book

task: select-document-type
project-id: existing-env-book
document-type: book
```

ตรวจแล้วตอบ

```text
อนุมัติประเภทเอกสาร
```

---

### ขั้นที่ 2: นำเข้า DOCX

```text
ใช้ skill write-thai-academic-book

task: import-manuscript
project-id: existing-env-book
input: D:\งาน\ต้นฉบับหนังสือ.docx
```

ระบบจะ

- copy DOCX เดิมไปเก็บที่ `source/original-manuscript.docx`
- คำนวณ SHA-256 เพื่อยืนยันว่าไฟล์ต้นฉบับไม่ถูกแก้
- แยกบทจาก Heading 1 หรือหัวข้อ `บทที่ N`
- สร้างรายงาน `source/import-report.md`

ตรวจรายงานแล้วตอบ

```text
อนุมัติการนำเข้า
```

---

### ขั้นที่ 3: ตรวจ QC ทั้งต้นฉบับ

```text
ใช้ skill write-thai-academic-book

task: manuscript-qc
project-id: existing-env-book
```

ระบบควรสร้าง

```text
final/manuscript-preflight-report.md
final/manuscript-qc.md
chapters/chapter-NN/chapter-qc.md
chapters/chapter-NN/sources-and-rights.md
final/approval.md
```

หากต้องแก้ ให้ตอบ

```text
แก้ตาม QC
```

---

### ขั้นที่ 4: แก้ต้นฉบับตาม QC

```text
ใช้ skill write-thai-academic-book

task: revise-manuscript
project-id: existing-env-book
```

ระบบต้องไม่เขียนทับ `source/original-manuscript.docx` แต่ควรสร้างไฟล์ใหม่ เช่น

```text
final/revised-manuscript.docx
final/revision-log.md
```

ตรวจแล้วตอบ

```text
อนุมัติฉบับแก้ไข
```

---

### ขั้นที่ 5: Final QC และผลิตไฟล์

```text
ใช้ skill write-thai-academic-book

task: final-qc
project-id: existing-env-book
```

เมื่อผ่านและได้รับอนุมัติแล้ว

```text
ใช้ skill write-thai-academic-book

task: produce-document
project-id: existing-env-book
```

---

## Workflow C: มีร่างเฉพาะบท

ใช้เมื่อมีไฟล์ร่างบทหนึ่งอยู่แล้ว เช่น

```text
D:\งาน\ร่างบทที่-3.docx
```

ตัวอย่างคำสั่ง

```text
ใช้ skill write-thai-academic-book

task: draft-chapter 03
project-id: env-microbiology-book
input: D:\งาน\ร่างบทที่-3.docx
```

ในกรณีนี้ระบบควร

- ตรวจร่างเดิมก่อนแก้
- สร้าง `draft-audit.md`
- แยกรายการเป็น `retain`, `revise`, `add`, `remove`
- ปรับเฉพาะส่วนที่มีเหตุผลรองรับ
- ไม่เขียนใหม่ทั้งบทเพียงเพื่อเปลี่ยนสำนวน
- ไม่ใช้ไฟล์ `chapters/chapter-03/draft.md` เดิมเป็น user draft เพราะถือเป็น generated artifact

ผลลัพธ์ที่ควรได้

```text
chapters/chapter-03/draft-audit.md
chapters/chapter-03/draft.md
chapters/chapter-03/sources-and-rights.md
chapters/chapter-03/approval.md
```

---

## คำสั่ง task ทั้งหมด

| Task | ใช้เมื่อ | ผลลัพธ์หลัก | ต้องอนุมัติก่อนขั้นถัดไป |
|---|---|---|---|
| `select-document-type` | เริ่ม project และเลือกประเภทเอกสาร | `manuscript-profile.md`, `type-approval.md` | ใช่ |
| `project-setup` | สร้าง brief และ governing standard | `project-brief.md`, `governing-standard.md` | ใช่ |
| `refresh-sources` | อัปเดตคู่มือ/เกณฑ์เมื่อมีเอกสารใหม่ | `governing-standard.md` | ใช่ |
| `draft-outline` | ร่างโครงร่าง | `outline.md` | ใช่ |
| `outline-qc` | ตรวจโครงร่าง | `outline-qc.md` | ใช่ |
| `revise-outline` | แก้โครงร่างตาม QC | `outline.md` ฉบับแก้ | ใช่ |
| `draft-chapter <NN>` | ร่างบทใหม่หรือปรับร่างบทที่มี input | `draft.md`, `sources-and-rights.md` | ใช่ |
| `chapter-qc <NN>` | ตรวจคุณภาพบท | `chapter-qc.md` | ใช่ |
| `revise-chapter <NN>` | แก้บทตาม QC | `revision.md` | ใช่ |
| `import-manuscript` | นำเข้า DOCX เดิมทั้งเล่ม | `original-manuscript.docx`, `import-report.md` | ใช่ |
| `manuscript-qc` | ตรวจต้นฉบับนำเข้าทั้งเล่ม | `manuscript-qc.md` และ QC รายบท | ใช่ |
| `revise-manuscript` | แก้ต้นฉบับนำเข้าตาม QC | `revised-manuscript.docx`, `revision-log.md` | ใช่ |
| `final-qc` | ตรวจทั้งเล่มก่อนผลิตไฟล์ | `final-qc.md`, `preflight-report.md` | ใช่ |
| `produce-document` | ผลิตไฟล์สุดท้าย | `manuscript.docx`, `manuscript.pdf`, `rendered/` | ใช่ |

---

## โครงสร้างผลลัพธ์

ผลลัพธ์ถูกแยกเป็น 4 ระดับ ได้แก่ project, source, chapters และ final

```text
output/<project-id>/
├── project/
│   ├── manuscript-profile.md
│   ├── type-approval.md
│   ├── project-brief.md
│   ├── governing-standard.md
│   ├── outline.md
│   ├── outline-qc.md
│   └── approval.md
├── source/
│   ├── original-manuscript.docx
│   ├── import-report.md
│   └── approval.md
├── chapters/
│   └── chapter-01/
│       ├── draft.md
│       ├── draft-audit.md
│       ├── chapter-qc.md
│       ├── revision.md
│       ├── sources-and-rights.md
│       └── approval.md
└── final/
    ├── manuscript-qc.md
    ├── revised-manuscript.docx
    ├── revision-log.md
    ├── manuscript.docx
    ├── manuscript.pdf
    ├── manuscript-preflight-report.md
    ├── preflight-report.md
    ├── final-qc.md
    ├── rendered/
    └── approval.md
```

ข้อกำหนดสำคัญ

- ไฟล์ระดับ project ไม่ควรปะปนกับไฟล์รายบท
- แต่ละบทใช้โฟลเดอร์ `chapter-01`, `chapter-02`, ...
- ต้นฉบับเดิมต้องอยู่ใน `source/original-manuscript.docx`
- ไฟล์สุดท้ายอยู่ใน `final/`

---

## การใช้ไฟล์เกณฑ์หรือคู่มือของหน่วยงาน

repo นี้มีเกณฑ์สรุปใน `references/` เพื่อใช้เริ่มงาน แต่ไม่ได้รวม PDF ต้นฉบับของสถาบันหรือสำนักพิมพ์ เพราะสิทธิ์เผยแพร่อาจแตกต่างกัน

หากต้องใช้เกณฑ์ของมหาวิทยาลัย คณะ สำนักพิมพ์ หรือหน่วยงานเฉพาะ ควรส่งไฟล์คู่มือฉบับล่าสุดให้ระบบ แล้วเรียก

```text
ใช้ skill write-thai-academic-book

task: refresh-sources
project-id: env-microbiology-book
คู่มือ/เกณฑ์ที่เพิ่ม: <แนบไฟล์หรือระบุ path>
สิ่งที่ต้องใช้จากคู่มือ: เกณฑ์คุณภาพ รูปแบบเอกสาร องค์ประกอบที่ต้องมี และระดับคะแนน
```

ระบบควรอัปเดตเฉพาะ `project/governing-standard.md` และหยุดรออนุมัติ ไม่ควรเปลี่ยนประเภทเอกสารหรือแก้บทโดยอัตโนมัติ

---

## ตัวอย่าง prompt ใช้งานจริง

### ตัวอย่าง 1: หนังสือใหม่

```text
ใช้ skill write-thai-academic-book

task: select-document-type
project-id: env-microbiology-book
document-type: book
```

```text
อนุมัติประเภทเอกสาร
```

```text
ใช้ skill write-thai-academic-book

task: project-setup
project-id: env-microbiology-book
หัวข้อ: การประยุกต์ใช้จุลินทรีย์เพื่อฟื้นฟูสิ่งแวดล้อม
กลุ่มผู้อ่าน: นักศึกษาปริญญาตรีตอนปลาย บัณฑิตศึกษา นักวิชาการสิ่งแวดล้อม และผู้ปฏิบัติงานด้านสิ่งแวดล้อม
ขอบเขต: หลักการและกรณีศึกษาการใช้จุลินทรีย์ สาหร่าย และไซยาโนแบคทีเรียในการฟื้นฟูสิ่งแวดล้อม น้ำเสีย ดินปนเปื้อน และระบบชุมชน
หลักฐานและแหล่งข้อมูลที่มี: เอกสารสอนเดิม บทความวิจัยของผู้เขียน บทความ review และกรณีศึกษาชุมชน
```

---

### ตัวอย่าง 2: ตำราที่ผูกกับรายวิชา

```text
ใช้ skill write-thai-academic-book

task: select-document-type
project-id: phycology-textbook
document-type: textbook
```

```text
อนุมัติประเภทเอกสาร
```

```text
ใช้ skill write-thai-academic-book

task: project-setup
project-id: phycology-textbook
หัวข้อ: สาหร่ายวิทยาและโพรโทซัววิทยา
รายวิชา: 215312 สาหร่ายวิทยาและโพรโทซัววิทยา
กลุ่มผู้อ่าน: นักศึกษาปริญญาตรีสาขาจุลชีววิทยา ชั้นปีที่ 4
ขอบเขต: อนุกรมวิธาน สัณฐานวิทยา นิเวศวิทยา การเพาะเลี้ยง และการประยุกต์ใช้สาหร่าย ไซยาโนแบคทีเรีย และโพรโทซัว
หลักฐานรายวิชา: CLO, PLO mapping, แผนการสอน, รายการ lab และกิจกรรมภาคสนาม
```

---

### ตัวอย่าง 3: นำเข้าต้นฉบับเดิม

```text
ใช้ skill write-thai-academic-book

task: import-manuscript
project-id: env-book-existing
input: D:\งาน\ต้นฉบับสิ่งแวดล้อม.docx
```

---

### ตัวอย่าง 4: ร่างบทจากไฟล์เดิมเฉพาะบท

```text
ใช้ skill write-thai-academic-book

task: draft-chapter 04
project-id: env-microbiology-book
input: D:\งาน\ร่างบทที่4.docx
```

---

### ตัวอย่าง 5: ตรวจขั้นสุดท้าย

```text
ใช้ skill write-thai-academic-book

task: final-qc
project-id: env-microbiology-book
chapter-count: 8
```

---

## ข้อควรระวัง

### อย่ารวมหลาย task ในคำสั่งเดียว

ไม่ควรสั่งแบบนี้

```text
ช่วยเลือกประเภท สร้าง outline ร่างบทที่ 1 และทำ QC ให้เลย
```

ควรแยกเป็น

```text
task: select-document-type
```

รออนุมัติ แล้วค่อยเรียก

```text
task: project-setup
```

---

### อย่าเริ่มบทถัดไปก่อนบทก่อนหน้าผ่าน gate

บทที่ 2 ควรเริ่มได้ต่อเมื่อบทที่ 1 ผ่านกระบวนการที่กำหนดและได้รับอนุมัติแล้ว

---

### อย่าใช้ generated draft เป็น user draft

ไฟล์ใน

```text
chapters/chapter-NN/draft.md
```

เป็น artifact ที่ระบบสร้าง ไม่ใช่ user draft หากต้องการให้ระบบปรับร่างของผู้ใช้ ต้องระบุไฟล์ต้นทางภายนอก เช่น DOCX, MD, TXT หรือ PDF ที่ผู้ใช้เตรียมไว้

---

### อย่าให้ระบบสร้างหลักฐานที่ไม่มีจริง

หากไม่มี citation, permission, author experience, course evidence หรือหลักฐานระดับ A ให้ระบบระบุเป็น blocker แทนการแต่งข้อมูล

---

## การแก้ปัญหาที่พบบ่อย

### 1. ระบบบอกว่า task ถูก block เพราะยังไม่ได้เลือกประเภทเอกสาร

ให้เริ่มจาก

```text
task: select-document-type
project-id: <project-id>
document-type: book
```

หรือเลือก `teaching-notes` / `textbook` ตามงานจริง

---

### 2. ระบบบอกว่า approval ยังเป็น `PENDING`

ต้องตอบอนุมัติ task ล่าสุดก่อน เช่น

```text
อนุมัติ
```

หรือหากต้องแก้ตาม QC ให้ตอบ

```text
แก้ตาม QC
```

---

### 3. นำเข้า DOCX แล้วตรวจไม่พบบท

ตรวจว่าต้นฉบับมีหัวข้อระดับบทแบบใดแบบหนึ่ง

```text
บทที่ 1 ...
บทที่ 2 ...
```

หรือใช้ Heading 1 ที่มีเลขบทชัดเจน

หากเลขบทซ้ำ ข้ามลำดับ หรือไม่มีเลขบท ระบบไม่ควรเดาเอง ให้แก้ไฟล์ต้นฉบับก่อนนำเข้าใหม่ใน project ใหม่หรือ rebuild โดยมีคำสั่งชัดเจน

---

### 4. produce-document ไม่ทำงาน

ตรวจว่า

- ผ่าน `final-qc` แล้ว
- `final/approval.md` เป็น `APPROVED`
- `final-qc.md` มี target decision เป็น `MEETS_TARGET`
- blocker count เป็น 0
- มีข้อมูล `chapter-count` หากเป็น workflow เขียนใหม่

---

### 5. ต้องเปลี่ยนประเภทเอกสารกลางคัน

ไม่ควรแก้ `manuscript-profile.md` เอง ควรสร้าง project-id ใหม่ หรือสั่ง rebuild/change request อย่างชัดเจน เพราะประเภทเอกสารมีผลต่อเกณฑ์ คุณภาพ เป้าหมาย และ artifact ทั้งหมด

---

## หมายเหตุสำหรับผู้พัฒนา

### ตำแหน่ง script สำคัญ

```text
plugins/write-thai-academic-book/skills/write-thai-academic-book/scripts/
├── check_task_gate.py
├── import_manuscript.py
└── preflight.py
```

### ตัวอย่างตรวจ gate ด้วยตนเอง

```powershell
python scripts/check_task_gate.py --project-root output/env-microbiology-book --task select-document-type --document-type book
```

```powershell
python scripts/check_task_gate.py --project-root output/env-microbiology-book --task draft-chapter --chapter 1 --document-type book
```

```powershell
python scripts/check_task_gate.py --project-root output/env-microbiology-book --task final-qc --chapter-count 8 --document-type book
```

### ตัวอย่าง preflight

```powershell
python scripts/preflight.py --type book --input output/env-microbiology-book --output output/env-microbiology-book/final/preflight-report.md
```

preflight เป็นการตรวจโครงสร้างและความสอดคล้องที่ตรวจจับได้เท่านั้น ไม่สามารถยืนยันความถูกต้องทางวิชาการ ความเป็นต้นฉบับ สิทธิ์การใช้ภาพ หรือการผ่านเกณฑ์สถาบันได้ทั้งหมด จึงต้องตามด้วย QC เชิงวิชาการและการตรวจของผู้ใช้เสมอ

---

---

## License

### Academic and Non-Profit Use Only

Copyright (c) 2026 Chayakorn Pumas / rijjina contributors

This repository, including the `write-thai-academic-book` skill, prompts, templates, scripts, examples, documentation, and related assets, is provided for **academic, educational, research, and non-profit use only**.

You may use, copy, install, study, modify, and adapt this project for the following permitted purposes:

- teaching, learning, academic writing, curriculum development, research, and scholarly work;
- internal use by schools, universities, public research organizations, government institutions, charities, and other non-profit organizations;
- personal non-commercial study, experimentation, and academic productivity;
- adaptation for non-profit training, workshops, or institutional academic workflows, provided that attribution is retained.

You may not use this project, in whole or in part, for commercial purposes without prior written permission from the copyright holder. Prohibited commercial uses include, but are not limited to:

- selling this project, modified versions, templates, prompts, scripts, or packaged derivatives;
- using this project as part of a paid SaaS, subscription service, commercial writing service, consulting package, or commercial AI product;
- redistributing this project as part of a commercial training course, paid software bundle, or for-profit institutional service;
- removing attribution, license notices, or copyright notices.

Academic publication, public-sector work, externally funded research, and university-funded activity are allowed when the primary purpose remains academic, educational, research-oriented, or non-profit rather than commercial resale or commercial service delivery.

Commercial licensing may be requested by contacting the repository owner.

This project is provided **as is**, without warranty of any kind, express or implied. The authors and contributors are not liable for any claim, damage, data loss, academic evaluation outcome, publication decision, or other liability arising from the use of this project.

Third-party libraries, tools, models, platforms, and dependencies remain subject to their own licenses and terms of use.

> Note: This is a non-commercial / academic-use license. It should not be described as an OSI-approved open-source license.
