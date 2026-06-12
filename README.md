# Write Thai Academic Book

Skill สำหรับช่วยร่าง ตรวจ และปรับปรุงงานวิชาการภาษาไทย 3 ประเภท ได้แก่

- `เอกสารคำสอน` เป้าหมายคุณภาพภายในระดับ A-equivalent
- `หนังสือ` เป้าหมายระดับ A
- `ตำรา` เป้าหมายระดับ A

ระบบทำงานแบบ **ครั้งละหนึ่ง task** ใช้ไฟล์งานเดิมเป็นหลัก แยกผลลัพธ์รายบท และหยุดรอการอนุมัติจากผู้ใช้ก่อนเริ่มขั้นถัดไป จึงช่วยลดปัญหาการร่างต่อเนื่องผิดลำดับ การสร้างข้อมูลซ้ำ และการเขียนทับต้นฉบับเดิม

## ความสามารถหลัก

- กำหนดประเภทเอกสารและเกณฑ์ที่ใช้ก่อนเริ่มงาน
- สร้าง project brief และ governing standard
- ร่างและตรวจโครงร่างโดยแยกเป็นคนละ task
- ร่าง ตรวจ และแก้ไขทีละบท
- นำเข้าต้นฉบับ DOCX เดิมเพื่อตรวจและปรับปรุง
- ตรวจคุณภาพทั้งเล่มตามเป้าหมาย A หรือ A-equivalent
- ผลิต DOCX/PDF หลังผ่าน QC และได้รับอนุมัติ
- บันทึกสถานะ `PENDING`, `APPROVED` และ `CHANGES_REQUESTED`

## การติดตั้ง

### Codex

ขอให้ Codex ใช้ `$skill-installer` ติดตั้งจาก repo นี้:

```text
https://github.com/rijjina/book_drafter
```

หรือ clone แล้วติดตั้งด้วย PowerShell:

```powershell
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
.\scripts\install.ps1 -Target codex
```

Skill จะถูกติดตั้งที่ `~/.agents/skills/write-thai-academic-book`

### Claude Cowork

ติดตั้งแบบ marketplace:

1. เปิด **Customize > Plugins**
2. เลือก **Add marketplace > Add from a repository**
3. ใส่ URL `https://github.com/rijjina/book_drafter`
4. เลือกติดตั้ง `write-thai-academic-book` จาก marketplace ชื่อ `thai-academic-writing`

หากต้องการ upload เป็น skill โดยตรง ให้ดาวน์โหลดไฟล์:

[`packages/write-thai-academic-book.zip`](packages/write-thai-academic-book.zip)

แล้วนำเข้าใน **Customize > Skills**

### Google Antigravity

```powershell
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
.\scripts\install.ps1 -Target antigravity
```

สำหรับ Antigravity CLI:

```powershell
.\scripts\install.ps1 -Target antigravity-cli
```

### macOS หรือ Linux

```bash
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
./scripts/install.sh codex
```

เปลี่ยน argument เป็น `antigravity`, `antigravity-cli` หรือ `claude-code` ตามระบบที่ใช้

## หลักการใช้งาน

1. หนึ่งคำสั่งทำได้เพียงหนึ่ง task
2. ทุก task สร้างเฉพาะ artifact ที่อยู่ในความรับผิดชอบของ task นั้น
3. เมื่อ task เสร็จ ระบบตั้งสถานะเป็น `PENDING` และหยุด
4. ผู้ใช้ต้องตรวจผลและตอบอนุมัติหรือขอแก้ไข
5. ระบบบันทึกการอนุมัติลง `approval.md` ก่อนเปิด task ถัดไป
6. ผล `PASS` หรือ `MEETS_TARGET` จากระบบไม่ถือเป็นการอนุมัติของมนุษย์

คำตอบเช่น `อนุมัติ`, `ผ่าน`, `โอเค`, `ไปต่อ` ใช้อนุมัติเฉพาะ task ล่าสุดเท่านั้น

## เริ่มโครงการใหม่

### 1. เลือกประเภทเอกสาร

คำสั่งแรกต้องระบุประเภทหนึ่งประเภท:

```text
ใช้ skill write-thai-academic-book
task: select-document-type
project-id: my-book
document-type: book
```

ค่าที่ใช้ได้:

| ประเภท | ค่าในคำสั่ง | ต้องเชื่อมรายวิชา | เป้าหมาย |
| --- | --- | --- | --- |
| เอกสารคำสอน | `teaching-notes` | ต้องเชื่อม | A-equivalent |
| หนังสือ | `book` | ไม่บังคับ | A |
| ตำรา | `textbook` | ต้องเชื่อม | A |

หนังสือไม่จำเป็นต้องมี มคอ.3 รหัสวิชา CLO/PLO หรือหลักฐานภาระสอน ส่วนตำราและเอกสารคำสอนต้องมีข้อมูลรายวิชาตามเกณฑ์ที่เกี่ยวข้อง

### 2. อนุมัติประเภท

หลังระบบสร้าง `manuscript-profile.md` ให้ตรวจแล้วตอบ:

```text
อนุมัติประเภทเอกสาร
```

### 3. สร้างข้อมูลโครงการ

```text
ใช้ skill write-thai-academic-book
task: project-setup
project-id: my-book
หัวข้อ: ...
กลุ่มผู้อ่าน: ...
ขอบเขต: ...
หลักฐานและแหล่งข้อมูลที่มี: ...
```

ระบบจะสร้าง project brief และ governing standard แล้วหยุดรออนุมัติ

### 4. ร่างและตรวจโครงร่าง

เรียกทีละ task ตามลำดับ:

```text
task: draft-outline
project-id: my-book
```

ตรวจและอนุมัติโครงร่าง จากนั้นจึงเรียก:

```text
task: outline-qc
project-id: my-book
```

หากต้องแก้ ให้ตอบ `แก้ตาม QC` แล้วเรียก `revise-outline` ห้ามรวมการร่าง ตรวจ และแก้ไว้ในคำสั่งเดียว

### 5. ทำงานทีละบท

```text
task: draft-chapter 01
project-id: my-book
```

เมื่ออนุมัติร่างแล้ว:

```text
task: chapter-qc 01
project-id: my-book
```

หาก QC ขอแก้ไข:

```text
แก้ตาม QC
task: revise-chapter 01
project-id: my-book
```

บทที่ 2 จะเริ่มได้ต่อเมื่อบทที่ 1 ผ่านกระบวนการและได้รับอนุมัติตาม gate แล้ว

## กรณีมีต้นฉบับเดิม

ใช้เส้นทางนี้เมื่อมีไฟล์ DOCX ที่ร่างไว้แล้ว:

```text
select-document-type
→ import-manuscript
→ manuscript-qc
→ revise-manuscript
→ final-qc
→ produce-document
```

ตัวอย่าง:

```text
ใช้ skill write-thai-academic-book
task: import-manuscript
project-id: my-book
input: D:\งาน\ต้นฉบับ.docx
```

ระบบจะเก็บต้นฉบับเดิมแบบไม่แก้ไขไว้ที่ `source/original-manuscript.docx` และสร้างรายงานนำเข้า ก่อนหยุดรออนุมัติ

`manuscript-qc` จะตรวจช่องว่างรายบทและทั้งเล่ม ส่วน `revise-manuscript` จะแก้เฉพาะรายการที่ผู้ใช้อนุมัติ พร้อมสร้าง `revised-manuscript.docx` และ `revision-log.md` โดยไม่เขียนทับไฟล์ต้นฉบับ

## กรณีมีร่างเฉพาะบท

สามารถส่งไฟล์ร่างของบทให้ `draft-chapter` ได้:

```text
task: draft-chapter 03
project-id: my-book
input: D:\งาน\ร่างบทที่-3.docx
```

ระบบจะตรวจร่างก่อน แยกรายการ `retain`, `revise`, `add`, `remove` ไว้ใน `draft-audit.md` แล้วปรับเฉพาะส่วนที่มีเหตุผลรองรับ ไม่เขียนใหม่ทั้งบทเพียงเพื่อเปลี่ยนสำนวน

## การตรวจขั้นสุดท้าย

เมื่อทุกบทได้รับอนุมัติ:

```text
task: final-qc
project-id: my-book
chapter-count: 8
```

หากผล QC เป็น `MEETS_TARGET` และผู้ใช้อนุมัติ จึงเรียก:

```text
task: produce-document
project-id: my-book
```

ระบบจึงจะสร้าง DOCX, PDF, รายงาน preflight และไฟล์ render สำหรับตรวจหน้ากระดาษ

## โครงสร้างผลลัพธ์

```text
output/<project-id>/
├── project/     ข้อมูลโครงการ เกณฑ์ โครงร่าง และ approval
├── source/      ต้นฉบับเดิมและรายงานนำเข้า
├── chapters/    draft, QC, revision และแหล่งอ้างอิงแยกรายบท
└── final/       QC ทั้งเล่ม DOCX PDF และรายงานส่งมอบ
```

ไฟล์ระดับโครงการไม่ปะปนกับไฟล์รายบท แต่ละบทเขียนเฉพาะใน `chapters/chapter-NN/`

## Task ที่รองรับ

- `select-document-type`
- `project-setup`
- `refresh-sources`
- `draft-outline`
- `outline-qc`
- `revise-outline`
- `draft-chapter <NN>`
- `chapter-qc <NN>`
- `revise-chapter <NN>`
- `import-manuscript`
- `manuscript-qc`
- `revise-manuscript`
- `final-qc`
- `produce-document`

## หมายเหตุเรื่องคู่มือและเกณฑ์

แพ็กเกจใน repo นี้ไม่ได้รวม PDF ต้นฉบับของสถาบันหรือสำนักพิมพ์ เนื่องจากสิทธิ์เผยแพร่อาจแตกต่างกัน ภายใน skill มีเกณฑ์สรุปสำหรับเริ่มงาน ผู้ใช้ควรส่งคู่มือฉบับปัจจุบันและเรียก `refresh-sources` เมื่อต้องอ้างอิงข้อความเฉพาะหรือใช้ข้อกำหนดของหน่วยงาน
