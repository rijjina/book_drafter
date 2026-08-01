# Thai Academic Writing Suite

ชุด Cross-platform Agent Skills สำหรับค้นหลักฐาน วางแผน ประเมิน ร่าง แก้ไข
และผลิตต้นฉบับงานวิชาการภาษาไทย โดยรองรับ:

- `teaching-notes` — เอกสารคำสอน เป้าหมายภายใน A-equivalent
- `book` — หนังสือ เป้าหมายระดับ A
- `textbook` — ตำรา เป้าหมายระดับ A

รุ่น `1.3.0` ใช้ Skill 4 ตัวร่วมกันบน Codex, Claude Cowork,
Claude Code และ Google Antigravity โดยมี manifest และตัวติดตั้งบาง ๆ สำหรับ
แต่ละ host ไม่แยกสำเนา workflow จึงลดปัญหาเนื้อหาและ gate ไม่ตรงกัน

| Skill | หน้าที่ |
| --- | --- |
| `orchestrate-thai-academic-writing` | กำกับ flow และตรวจ handoff ระหว่างสกิล |
| `write-thai-academic-book` | ตั้งโครงการ ร่าง/แก้ต้นฉบับ และผลิต DOCX ตาม approval gate |
| `research-outline-evidence` | ค้นหลักฐานแบบ local-first และสร้าง claim–evidence handoff |
| `assess-thai-academic-manuscript` | ประเมิน outline รายบท ทั้งเล่ม และ route readiness โดยไม่แก้ต้นฉบับ |

`build-outline-matrix` และ `thai-academic-teaching-material` เป็น companion skills
ที่ติดตั้งแยกต่างหากและถูกเรียกผ่าน artifact contract ของ orchestrator

[คู่มือภาษาไทยฉบับละเอียด](README-Lium-notebook.md)

## Compatibility

| Platform | รูปแบบที่รองรับ | วิธีติดตั้งแนะนำ |
| --- | --- | --- |
| Codex app, CLI และ IDE | Agent Skill และ Codex plugin | Repo marketplace หรือ `~/.agents/skills` |
| Claude Cowork / Claude Desktop | Claude plugin marketplace หรือ Skill ZIP | Add repository หรือ upload ZIP |
| Claude Code | Skill หรือ Claude plugin | `~/.claude/skills` หรือ marketplace |
| Antigravity IDE | Agent Skill หรือ Antigravity plugin | `~/.gemini/config/skills` หรือ `~/.gemini/config/plugins` |
| Antigravity CLI | Antigravity plugin | `agy plugin install` หรือ `~/.gemini/antigravity-cli/plugins` |

โครงสร้างหลักเป็นไปตาม Agent Skills แบบ progressive disclosure:
`SKILL.md` มี `name` และ `description`; รายละเอียดแยกอยู่ใน `references/`;
คำสั่งที่ต้องทำซ้ำอยู่ใน `scripts/`; template อยู่ใน `assets/`.

เอกสารรูปแบบจากผู้ให้บริการ:

- [OpenAI: Build skills](https://developers.openai.com/codex/skills/)
- [OpenAI: Package a plugin](https://developers.openai.com/codex/plugins/build/)
- [Anthropic: Create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Anthropic: Plugin marketplaces](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces)
- [Google Antigravity: Skills](https://antigravity.google/docs/skills)
- [Google Antigravity: Plugins](https://antigravity.google/docs/plugins)

## Workflow หลัก

```text
Project brief → Outline → Assessment → Research SCOPING
→ Six-column Outline Matrix → Research GAP_FILL (ถ้าจำเป็น)
→ READY_TO_DRAFT → Draft chapter → Assessment → Author approval
→ Approved revision → Manuscript assessment → Final QC → DOCX
```

กฎสำคัญ: research ไม่แก้ Matrix, assessment ไม่แก้ต้นฉบับ,
writer แก้เฉพาะ `RV-xxx` ที่ผู้เขียนอนุมัติ และเริ่มร่างได้เมื่อ Matrix เป็น
`READY_TO_DRAFT` พร้อม Evidence Package ที่ fingerprint ตรงกันเท่านั้น

## สิ่งที่ชุด Skill ทำ

- บังคับเลือกประเภทผลงานและเป้าหมายคุณภาพก่อนเริ่ม production
- ทำงานครั้งละหนึ่ง gate-bearing task
- ใช้ artifact เดิมและแหล่งข้อมูลที่ตรวจสอบได้เป็นหลัก
- แยก planning, drafting, QC, revision และ production ออกจากกัน
- รักษาสำนวนผู้เขียนด้วย deterministic style profile
- รองรับ review-only ที่ผู้เขียนนำข้อเสนอแนะไปแก้เอง
- ใช้ Markdown เป็น editable source และสร้าง DOCX เฉพาะ final gate
- ไม่สร้าง citation, permission, author experience หรือหลักฐานคุณภาพขึ้นเอง

## โครงสร้าง Repository

```text
book_drafter/
├── .agents/plugins/marketplace.json       # Codex repo marketplace
├── .claude-plugin/marketplace.json        # Claude/Cowork marketplace
├── packages/                              # Direct Skill ZIPs (4 files)
├── plugins/write-thai-academic-book/
│   ├── .codex-plugin/plugin.json          # Codex plugin adapter
│   ├── .claude-plugin/plugin.json         # Claude plugin adapter
│   ├── plugin.json                        # Antigravity plugin adapter
│   └── skills/                            # Shared canonical Skill payloads
│       ├── write-thai-academic-book/
│       ├── research-outline-evidence/
│       ├── assess-thai-academic-manuscript/
│       └── orchestrate-thai-academic-writing/
└── scripts/
    ├── install.ps1
    ├── install.sh
    └── validate_distribution.py
```

Host-specific files เป็น adapter เท่านั้น เนื้อหา workflow อยู่ใน
`plugins/write-thai-academic-book/skills/`

## การติดตั้ง

### Codex — Plugin marketplace

เหมาะเมื่อใช้ Codex app และต้องการให้ plugin ปรากฏใน Plugins Directory:

```text
codex plugin marketplace add rijjina/book_drafter --ref main
codex plugin add write-thai-academic-book@thai-academic-writing
```

เริ่ม task ใหม่หลังติดตั้งเพื่อให้ Codex โหลด skill รุ่นล่าสุด

### Codex — Standalone user Skill

Windows:

```powershell
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
.\scripts\install.ps1 -Target codex
```

macOS/Linux:

```bash
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
./scripts/install.sh codex
```

ติดตั้งที่ `~/.agents/skills/write-thai-academic-book` ซึ่ง Codex รองรับเป็น
user-level Skill

### Claude Cowork / Claude Desktop

วิธี plugin marketplace:

1. เปิด `Customize > Plugins`
2. เลือกเพิ่ม marketplace จาก repository
3. ระบุ `https://github.com/rijjina/book_drafter`
4. ติดตั้ง `write-thai-academic-book` จาก `thai-academic-writing`

วิธี Skill โดยตรง:

1. ดาวน์โหลด Skill ZIP ที่ต้องการจาก [`packages/`](packages/) หรือทั้ง 4 ไฟล์เพื่อใช้ workflow ครบชุด
2. เปิด `Customize > Skills`
3. Upload ZIP และเปิดใช้งาน Skill

Cowork ต้องเปิด code execution จึงจะเรียก Python scripts ได้ หากไม่มี
code execution ยังใช้ planning และ read-only review ได้ แต่ DOCX production
ต้องคงสถานะ blocked

### Claude Code

```powershell
.\scripts\install.ps1 -Target claude-code
```

หรือ:

```bash
./scripts/install.sh claude-code
```

ติดตั้งทั้ง 4 สกิลที่ `~/.claude/skills/`

### Google Antigravity IDE

ติดตั้งเป็น global Skill:

```powershell
.\scripts\install.ps1 -Target antigravity
```

ปลายทางคือ `~/.gemini/config/skills/<skill-name>` สำหรับทั้ง 4 สกิล

ติดตั้งเป็น global plugin ซึ่งรวม Skill payload:

```powershell
.\scripts\install.ps1 -Target antigravity-plugin
```

ปลายทางคือ `~/.gemini/config/plugins/write-thai-academic-book`

สำหรับ workspace เฉพาะ ให้คัดลอกโฟลเดอร์ Skill ไปยัง:

```text
<workspace>/.agents/skills/<skill-name>/
```

### Google Antigravity CLI

ติดตั้งจาก checkout โดยตรง:

```text
agy plugin install ./plugins/write-thai-academic-book
```

หรือใช้ตัวติดตั้ง:

```powershell
.\scripts\install.ps1 -Target antigravity-cli
```

```bash
./scripts/install.sh antigravity-cli
```

ปลายทางคือ `~/.gemini/antigravity-cli/plugins/write-thai-academic-book`

## Runtime Dependencies

Gate, import, preflight และ style extraction ใช้ Python standard library เป็นหลัก
การผลิตและตรวจ DOCX ต้องใช้ Python 3.10+ และ:

```text
Pillow>=10
PyYAML>=6
python-docx>=1.1
```

ติดตั้งเมื่อ host ไม่มี document runtime ให้มา:

```text
python -m pip install -r plugins/write-thai-academic-book/skills/write-thai-academic-book/requirements.txt
```

ไม่ต้องติดตั้ง dependency เพื่อใช้ review-only ที่ไม่เรียก scripts

## Quick Start

เริ่มทุกโครงการด้วยการเลือกประเภทเพียงหนึ่งประเภท:

```text
Use write-thai-academic-book.
task: select-document-type
project-id: my-book
document-type: book
```

ตรวจ `manuscript-profile.md` แล้วอนุมัติก่อนเรียก task ถัดไป:

```text
task: project-setup
project-id: my-book
หัวข้อ: ...
กลุ่มผู้อ่าน: ...
ขอบเขต: ...
หลักฐานที่มี: ...
```

จากนั้นทำทีละ gate:

```text
draft-outline → outline-qc → revise-outline (เมื่อมี CHANGES_REQUESTED)
draft-chapter 01 → chapter-qc 01 → revise-chapter 01
final-qc → explicit approval + Deliverable: DOCX → produce-document
```

กรณีมี DOCX เดิมทั้งเล่ม:

```text
select-document-type
→ import-manuscript
→ manuscript-qc
→ revise-manuscript
→ final-qc
→ produce-document
```

## Tasks

| กลุ่ม | Tasks |
| --- | --- |
| Project | `select-document-type`, `project-setup`, `refresh-sources`, `draft-outline`, `outline-qc`, `revise-outline` |
| Chapter | `draft-chapter <NN>`, `chapter-qc <NN>`, `revise-chapter <NN>` |
| Existing manuscript | `import-manuscript`, `manuscript-qc`, `revise-manuscript` |
| Author edits | `author-review [<NN>]` |
| Final | `final-qc`, `produce-document` |

## Approval และความปลอดภัย

- `PASS`, `CONDITIONAL PASS` และ `MEETS_TARGET` ไม่ใช่ human approval
- Approval ของ task หรือบทหนึ่งไม่ใช้แทนอีก task หรืออีกบท
- Revision ต้องมี `CHANGES_REQUESTED`
- Export ต้องมี `MEETS_TARGET`, `Status: APPROVED` และ `Deliverable: DOCX`
- `produce-document` สร้างเพียง `final/manuscript.docx`
- ไม่มี task ใดสร้าง final PDF
- ห้ามเขียนทับไฟล์ต้นฉบับของผู้ใช้
- สิทธิ์ filesystem/shell ของ host ไม่ถือเป็น approval ทางวิชาการ

## สำหรับผู้พัฒนา

ผู้ดูแลต้องแก้ canonical local Skill ก่อน แล้วใช้ `scripts/package_skill.py`
จาก canonical source สร้าง plugin payload และ ZIP ห้ามแก้ไฟล์ใน ZIP โดยตรง

ตรวจ distribution:

```text
python scripts/validate_distribution.py
python -m unittest discover -s plugins/write-thai-academic-book/skills/write-thai-academic-book/tests -p "test_*.py"
```

Public package ไม่รวม source PDFs, extraction cache, `__pycache__` หรือ
intermediate render files

## License

Academic and non-profit use only ดูรายละเอียดที่ [LICENSE.md](LICENSE.md)

ไม่ใช่ OSI-approved open-source license และการใช้เชิงพาณิชย์ต้องได้รับอนุญาต
จากเจ้าของลิขสิทธิ์ก่อน
