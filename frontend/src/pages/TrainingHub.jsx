import React, { useState } from 'react'

const QUIZ_QUESTIONS = [
  {
    id: 1,
    category: 'AgriShield™ Entity Safety',
    question: "A field advisory mentions 'Propiconazole 25% EC' and 'PM-KISAN'. How does VaaniSetu prevent these technical and chemical terms from being distorted?",
    options: [
      { text: "It relies on external online cloud translators", correct: false, explain: "VaaniSetu runs 100% offline with zero cloud dependency." },
      { text: "AgriShield™ regex shields 120+ domain entities inside protected tags before translation and restores them verbatim", correct: true, explain: "Correct! AgriShield™ uses tokenized protection to guarantee chemical dosages and government scheme names are 100% preserved." },
      { text: "It translates every word literally word-by-word", correct: false, explain: "Literal translation breaks chemical and biological meanings." },
      { text: "It prompts the user to manually re-type every acronym", correct: false, explain: "AgriShield™ performs automated rule-based preservation." }
    ]
  },
  {
    id: 2,
    category: 'Quality Gate & Review',
    question: "A translated advisory on 'Wheat Yellow Rust' receives an AI confidence score of 0.72 (🟡 Amber). What is the standard field procedure?",
    options: [
      { text: "Immediately broadcast the video to all farmer WhatsApp groups", correct: false, explain: "Amber advisories must always be verified before mass farmer dissemination." },
      { text: "Open the Review Queue, verify or edit the regional sentence, and click Approve to clear distribution and train Translation Memory", correct: true, explain: "Exactly! Approving corrections in the Review Queue clears distribution clearance and permanently trains Translation Memory at 98% confidence." },
      { text: "Delete the job and record the entire video from scratch", correct: false, explain: "No need to re-record; simply edit the single sentence in the web UI." },
      { text: "Ignore the alert because neural AI never makes mistakes", correct: false, explain: "The Confidence Gate specifically catches low-certainty terms." }
    ]
  },
  {
    id: 3,
    category: 'Last-Mile Telecom Delivery',
    question: "A BAIF field officer in a remote tribal belt wants to reach farmers who only possess basic ₹1,000 keypad phones without internet. Which format should be used?",
    options: [
      { text: "4K Subtitled Video MP4", correct: false, explain: "Basic feature phones cannot render MP4 videos or subtitles." },
      { text: "8kHz Mono Telephony Audio (.wav) for outbound automated IVR voice calls", correct: true, explain: "Spot on! VaaniSetu automatically encodes 8kHz telephony WAV audio compatible with basic GSM feature phones." },
      { text: "Formatted Word DOCX document", correct: false, explain: "Requires smartphone document apps and reading literacy." },
      { text: "Raw JSON timing manifests", correct: false, explain: "JSON manifests are internal system files." }
    ]
  },
  {
    id: 4,
    category: 'Air-Gapped Hardware & RAM Headroom',
    question: "Two training officers upload heavy video batches simultaneously on an 8GB RAM field laptop. How does VaaniSetu maintain system stability?",
    options: [
      { text: "It offloads compute to public cloud servers", correct: false, explain: "VaaniSetu is strictly 100% offline air-gapped." },
      { text: "The RAM-Aware Concurrency Planner throttles workers, serializes heavy AI inference with mutex locks, and preserves OS memory headroom", correct: true, explain: "Bravo! The dynamic resource planner dynamically calculates memory tiers and prevents OOM crashes." },
      { text: "It terminates other Windows operating system tasks", correct: false, explain: "VaaniSetu strictly respects user system resources." },
      { text: "It deletes earlier video files without permission", correct: false, explain: "Jobs are safely enqueued in SQLite WAL queue." }
    ]
  }
]

export default function TrainingHub() {
  const [activeTab, setActiveTab] = useState('trainer') // 'trainer' | 'reviewer' | 'it' | 'quiz'

  // Quiz State
  const [currentQ, setCurrentQ] = useState(0)
  const [selectedOption, setSelectedOption] = useState(null)
  const [score, setScore] = useState(0)
  const [quizFinished, setQuizFinished] = useState(false)
  const [officerName, setOfficerName] = useState('BAIF Field Officer')

  // Interactive Review Simulator State
  const [simEditedText, setSimEditedText] = useState('कॅल्शियम कार्बोनेटचा थर विरघळवण्यासाठी ठिबकच्या नळ्यांमध्ये १.५ किलो/सेंमी२ दाबाने ०.६% हायड्रोक्लोरिक आम्ल सोडून फ्लशिंग करावे.')
  const [simApproved, setSimApproved] = useState(false)

  // Interactive Voice Drill State
  const [drillPlayed, setDrillPlayed] = useState(false)

  const handleSelectOption = (idx) => {
    if (selectedOption !== null) return
    setSelectedOption(idx)
    if (QUIZ_QUESTIONS[currentQ].options[idx].correct) {
      setScore(s => s + 1)
    }
  }

  const handleNextQuestion = () => {
    if (currentQ < QUIZ_QUESTIONS.length - 1) {
      setCurrentQ(q => q + 1)
      setSelectedOption(null)
    } else {
      setQuizFinished(true)
    }
  }

  const handleRestartQuiz = () => {
    setCurrentQ(0)
    setSelectedOption(null)
    setScore(0)
    setQuizFinished(false)
  }

  return (
    <div style={{ maxWidth: 1080, margin: '0 auto', paddingBottom: 60 }}>
      {/* Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>🎓 BAIF Operational & Training Academy</h2>
          <p>Interactive mastery tracks, practical field drills, and verified AI practitioner certification</p>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <span className="badge green">100% Offline Ready</span>
          <span className="badge amber">BAIF Certified</span>
        </div>
      </div>

      {/* Role Navigation Tabs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 12,
        marginBottom: 24
      }}>
        {[
          { id: 'trainer', icon: '🌾', title: 'Field Extension Officer', sub: 'Prescriptions, WhatsApp & IVR' },
          { id: 'reviewer', icon: '🛡️', title: 'Content Reviewer', sub: 'Confidence Gate & Verification' },
          { id: 'it', icon: '⚙️', title: 'Air-Gapped IT Admin', sub: 'RAM Sizing & Offline Backups' },
          { id: 'quiz', icon: '🏆', title: 'Practitioner Certification', sub: '4-Step Competency Exam' },
        ].map(tab => (
          <div
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '14px 18px',
              borderRadius: 'var(--radius)',
              background: activeTab === tab.id ? 'var(--bg-surface)' : 'var(--bg-input)',
              border: activeTab === tab.id ? '1px solid var(--accent)' : '1px solid var(--border)',
              cursor: 'pointer',
              boxShadow: activeTab === tab.id ? '0 4px 16px rgba(0,0,0,0.3)' : 'none',
              transition: 'var(--transition)'
            }}
          >
            <div style={{ fontSize: 22, marginBottom: 6 }}>{tab.icon}</div>
            <div style={{ fontWeight: 700, fontSize: 14, color: activeTab === tab.id ? 'var(--accent)' : 'var(--text)' }}>
              {tab.title}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
              {tab.sub}
            </div>
          </div>
        ))}
      </div>

      {/* ── TRACK 1: FIELD EXTENSION OFFICER ── */}
      {activeTab === 'trainer' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>
          <div className="card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: 18, color: 'var(--text)' }}>
              🌾 Field Extension Officer Workflow Drill
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 20 }}>
              BAIF field officers rapidly generate multi-lingual farm advisories for crop emergencies, seasonal sowing guidelines, and livestock vaccinations.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', marginBottom: 4 }}>
                  Step 1: Pick 1-Click Scenario Preset or Paste Text
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  In the Upload Studio, click any Scenario Preset (e.g. 🌾 Wheat Yellow Rust Advisory) to auto-fill technical recommendations, chemical dilutions, and farmer context.
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', marginBottom: 4 }}>
                  Step 2: Multi-Language Target Selection
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  Select one or multiple target Indian languages (Hindi, Marathi, Gujarati, Telugu, Bengali, Kannada). The translation pipeline uses English pivot caching for zero duplicate compute.
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', marginBottom: 4 }}>
                  Step 3: Multi-Channel Farmer Dissemination
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  Export high-definition captioned video for WhatsApp broadcast, 8kHz mono WAV for feature phone outbound calls, and bilingual Word DOCX advisory cards.
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--text)' }}>
              📱 Interactive Last-Mile Preview Practice
            </h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
              Test how a farmer experiences an advisory broadcast on WhatsApp & IVR:
            </p>

            <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 10, border: '1px solid var(--border)', marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--green)', marginBottom: 6 }}>
                💬 WhatsApp Broadcast Message
              </div>
              <div style={{ fontSize: 12, color: 'var(--text)', background: 'rgba(0,0,0,0.3)', padding: 10, borderRadius: 6, lineHeight: 1.4 }}>
                🌱 <strong>BAIF कृषी सल्ला (मराठी)</strong><br />
                शेतकरी मित्रांनो, गहू पिकावरील पिवळा तांबेरा रोगाच्या तातडीच्या नियंत्रणासाठी प्रोपिकोनाझोल २५% ईसी १ मिली प्रति लिटर पाण्यात फवारावे.
              </div>
            </div>

            <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 10, border: '1px solid var(--border)' }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent)', marginBottom: 6 }}>
                📞 Feature Phone IVR Voice Broadcast
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '0 0 10px 0' }}>
                Simulating 8kHz mono telecom audio transmission for ₹1,000 keypad mobile phones.
              </p>
              <button
                className="btn btn-sm btn-secondary"
                onClick={() => setDrillPlayed(true)}
                style={{ width: '100%' }}
              >
                {drillPlayed ? '✓ IVR Telecom Stream Simulated' : '▶️ Test 8kHz Dialer Signal'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── TRACK 2: QUALITY GATEKEEPER & REVIEWER ── */}
      {activeTab === 'reviewer' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>
          <div className="card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: 18, color: 'var(--text)' }}>
              🛡️ Confidence Gatekeeper & Review Simulator
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 16 }}>
              Try human-in-the-loop verification on this amber-flagged drip irrigation advisory:
            </p>

            <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 8, border: '1px solid var(--border)', marginBottom: 16 }}>
              <div className="section-label" style={{ marginBottom: 6 }}>Original English Source</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                "Flush subsurface drip laterals with 0.6% hydrochloric acid at 1.5 kg/cm2 pressure to dissolve calcium scale."
              </div>
            </div>

            <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 8, border: '1px solid var(--border)', marginBottom: 16 }}>
              <div className="section-label" style={{ marginBottom: 6, color: 'var(--accent)' }}>Draft Marathi Translation (Edit & Validate)</div>
              <textarea
                className="text-input"
                rows={3}
                value={simEditedText}
                onChange={e => setSimEditedText(e.target.value)}
                style={{ marginBottom: 0 }}
              />
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button
                className="btn btn-primary"
                onClick={() => setSimApproved(true)}
                disabled={simApproved}
              >
                {simApproved ? '✓ Approved & Stored in TM (98%)' : '✓ Approve & Update Translation Memory'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => { setSimEditedText(''); setSimApproved(false); }}
              >
                Reset
              </button>
            </div>
          </div>

          <div className="card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--text)' }}>
              💡 Review Protocol Rules
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                🟢 <strong>Green (≥ 85%):</strong> High-confidence translation. Automatically cleared for farmer distribution.
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                🟡 <strong>Amber (65%–84%):</strong> Technical terms or complex grammar flagged for quick review in Review Queue.
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                🔴 <strong>Red (&lt; 65%):</strong> Marked as unverified; requires reviewer intervention before broadcast.
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4, borderTop: '1px solid var(--border)', paddingTop: 10 }}>
                ✦ <strong>Continuous Self-Learning:</strong> Every approved edit permanently updates SQLite Translation Memory (`translation_memory` table) so future translations never repeat errors.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TRACK 3: AIR-GAPPED IT ADMIN ── */}
      {activeTab === 'it' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <div className="card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: 18, color: 'var(--text)' }}>
              ⚙️ IT Administrator Operations Runbook
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', marginBottom: 4 }}>
                  1. Zero-Cloud Local Air-Gapped Deployment
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  Launch via <code>python launcher.py</code>. The server auto-detects hardware memory tiers (&lt;650MB peak RAM profile) and serves over local office LAN.
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', marginBottom: 4 }}>
                  2. Automated Workspace Recovery & Disk Sizing
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  Temporary audio chunks and intermediate frames in <code>C:\VaaniSetu\workspace\</code> auto-purge upon job completion. Packaged ZIPs are stored in <code>C:\VaaniSetu\outputs\</code>.
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', marginBottom: 4 }}>
                  3. Emergency Health Check & Database Backups
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  Run <code>python run_test_evidence.py</code> to execute the 12-test automated regression suite before field deployment.
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--text)' }}>
              🖥️ Hardware Memory Tier Reference
            </h3>
            <table className="data-table" style={{ fontSize: 12 }}>
              <thead>
                <tr>
                  <th>Memory Tier</th>
                  <th>RAM Profile</th>
                  <th>STT / NMT Engine</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Standard Production</strong></td>
                  <td>16GB+ RAM / GPU</td>
                  <td>Whisper Medium + IndicTrans2 Full</td>
                </tr>
                <tr>
                  <td><strong>Low-RAM Safe Profile</strong></td>
                  <td>8GB Field Laptop</td>
                  <td>Whisper Small + Piper ONNX Indic</td>
                </tr>
                <tr>
                  <td><strong>Ultra-Light Field Profile</strong></td>
                  <td>&lt;650MB Peak RAM</td>
                  <td>AgriShield™ JIT + TM Cache</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TRACK 4: PRACTITIONER CERTIFICATION EXAM ── */}
      {activeTab === 'quiz' && (
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="badge green">{QUIZ_QUESTIONS[currentQ]?.category || 'Certification'}</span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600 }}>
                Question {currentQ + 1} of {QUIZ_QUESTIONS.length}
              </div>
            </div>

            {!quizFinished ? (
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text)', marginBottom: 18, lineHeight: 1.4 }}>
                  {QUIZ_QUESTIONS[currentQ].question}
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
                  {QUIZ_QUESTIONS[currentQ].options.map((opt, idx) => {
                    let border = '1px solid var(--border)'
                    let bg = 'var(--bg-input)'
                    if (selectedOption !== null) {
                      if (opt.correct) {
                        border = '1px solid var(--green)'
                        bg = 'rgba(82, 196, 135, 0.15)'
                      } else if (selectedOption === idx) {
                        border = '1px solid var(--red)'
                        bg = 'rgba(239, 68, 68, 0.15)'
                      }
                    }

                    return (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleSelectOption(idx)}
                        style={{
                          padding: '12px 16px',
                          borderRadius: 8,
                          textAlign: 'left',
                          background: bg,
                          border: border,
                          color: 'var(--text)',
                          fontSize: 13,
                          cursor: selectedOption === null ? 'pointer' : 'default',
                          lineHeight: 1.4,
                          transition: 'var(--transition)'
                        }}
                      >
                        <strong>{String.fromCharCode(65 + idx)}.</strong> {opt.text}
                      </button>
                    )
                  })}
                </div>

                {selectedOption !== null && (
                  <div style={{
                    padding: 12,
                    borderRadius: 8,
                    background: QUIZ_QUESTIONS[currentQ].options[selectedOption].correct ? 'rgba(82, 196, 135, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid var(--border)',
                    marginBottom: 16,
                    fontSize: 12,
                    color: 'var(--text)'
                  }}>
                    💡 <strong>Rationale:</strong> {QUIZ_QUESTIONS[currentQ].options[selectedOption].explain}
                  </div>
                )}

                <button
                  type="button"
                  className="btn btn-primary"
                  style={{ width: '100%' }}
                  disabled={selectedOption === null}
                  onClick={handleNextQuestion}
                >
                  {currentQ < QUIZ_QUESTIONS.length - 1 ? 'Next Question ➔' : 'Complete Certification 🏆'}
                </button>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '16px 0' }}>
                <div style={{ fontSize: 44, marginBottom: 8 }}>🏆</div>
                <h3 style={{ fontSize: 20, fontWeight: 700, margin: '0 0 6px 0', color: 'var(--text)' }}>
                  BAIF AI Localization Practitioner Exam Complete!
                </h3>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
                  Score: <strong>{score} / {QUIZ_QUESTIONS.length}</strong> ({Math.round((score / QUIZ_QUESTIONS.length) * 100)}%)
                </p>

                {/* Printable Certificate */}
                <div style={{
                  background: 'linear-gradient(135deg, rgba(27,67,50,0.3) 0%, rgba(232,146,74,0.1) 100%)',
                  border: '2px solid var(--accent)',
                  borderRadius: 12,
                  padding: 24,
                  marginBottom: 20,
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--accent)', fontWeight: 700 }}>
                    Bharatiya Agro Industries Foundation (BAIF)
                  </div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, margin: '10px 0', color: 'var(--text)' }}>
                    Certificate of Competency — AI Rural Localization
                  </h2>
                  <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '0 0 12px 0' }}>
                    Presented to: <strong style={{ color: 'var(--text)' }}>{officerName}</strong>
                  </p>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)', fontFamily: 'monospace' }}>
                    Token: VAANI-BAIF-{Math.random().toString(36).substring(2, 8).toUpperCase()} · 100% Offline Validated
                  </div>
                </div>

                <div className="flex gap-2 justify-center">
                  <button type="button" className="btn btn-secondary" onClick={handleRestartQuiz}>
                    🔄 Retake Exam
                  </button>
                  <button type="button" className="btn btn-primary" onClick={() => window.print()}>
                    🖨️ Print Certificate
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
