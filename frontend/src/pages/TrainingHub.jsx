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

// Note: For larger applications, these track components could be moved to their own files.

const TrainerTrack = () => {
  const [trainerStep, setTrainerStep] = useState(0)
  const [drillPlayed, setDrillPlayed] = useState(false)

  return (
    <div className="card">
      <div className="page-header" style={{ padding: 0, border: 0, marginBottom: 16 }}>
        <h3 style={{ margin: 0, fontSize: 18, color: 'var(--text)' }}>
          👩‍🏫 Field Advisory Trainer: 3-Step Workflow
        </h3>
      </div>

      {/* Stepper */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {[0, 1, 2].map(step => (
          <div
            key={step}
            onClick={() => setTrainerStep(step)}
            style={{
              flex: 1,
              padding: '8px 10px',
              borderRadius: 6,
              border: `1px solid ${trainerStep === step ? 'var(--accent)' : 'var(--border)'}`,
              background: trainerStep === step ? 'rgba(74, 158, 122, 0.1)' : 'var(--bg-input)',
              cursor: 'pointer',
              fontSize: 12,
              fontWeight: 600,
              color: trainerStep === step ? 'var(--accent)' : 'var(--text-muted)',
              textAlign: 'center',
              transition: 'var(--transition)'
            }}
          >
            Step {step + 1}
          </div>
        ))}
      </div>

      {/* Step Content */}
      {trainerStep === 0 && (
        <div>
          <strong style={{ color: 'var(--text)', fontSize: 14 }}>1. Select Input & Languages</strong>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 4 }}>
            In the Advisory Studio, either select a 1-Click Scenario Preset (e.g., 'Lumpy Skin Disease Advisory'), or upload your own MP4 video / MP3 audio / DOCX script. Then, select the target regional languages for translation (e.g., Marathi, Gujarati).
          </p>
        </div>
      )}
      {trainerStep === 1 && (
        <div>
          <strong style={{ color: 'var(--text)', fontSize: 14 }}>2. Choose Delivery Pack & Localize</strong>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 4 }}>
            Select a delivery channel pack (e.g., 'WhatsApp & Mobile Pack'). This automatically configures the output formats. Click 'Start AI Localization' to begin the offline translation pipeline.
          </p>
        </div>
      )}
      {trainerStep === 2 && (
        <div>
          <strong style={{ color: 'var(--text)', fontSize: 14 }}>3. Preview, Verify, and Export</strong>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 4 }}>
            Use the interactive result hub to preview the bilingual transcript, play the translated audio/video, and simulate WhatsApp/IVR delivery. If the confidence score is green, download the final ZIP package for field distribution.
          </p>
        </div>
      )}

      {/* Interactive Voice Drill */}
      <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: 15, color: 'var(--text)' }}>
          🎙️ Practical Drill: Farmer Voice Query
        </h4>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 4, marginBottom: 12 }}>
          Listen to this authentic Marathi farmer query about sugarcane crops, then use the 'Farmer Voice → HQ English Bridge' mode in the Studio to transcribe and summarize it for BAIF Pune agronomists.
        </p>
        <audio
          controls
          src="/api/static/training_sample_marathi.wav"
          style={{ width: '100%', height: 40 }}
          onPlay={() => setDrillPlayed(true)}
        />
        {drillPlayed && (
          <div style={{ marginTop: 10, fontSize: 12, color: 'var(--green)', fontWeight: 500 }}>
            ✓ Great! Now head to the Advisory Studio and process this query.
          </div>
        )}
      </div>
    </div>
  )
}

const ReviewerTrack = () => {
  const [simEditedText, setSimEditedText] = useState('कॅल्शियम कार्बोनेटचा थर विरघळवण्यासाठी ठिबकच्या नळ्यांमध्ये १.५ किलो/सेंमी२ दाबाने ०.६% हायड्रोक्लोरिक आम्ल सोडून फ्लशिंग करावे.')
  const [simApproved, setSimApproved] = useState(false)
  const [showReviewRules, setShowReviewRules] = useState(false)

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20 }}>
      <div className="card">
        <h3 style={{ margin: '0 0 12px 0', fontSize: 18, color: 'var(--text)' }}>
          🛡️ Quality Reviewer: Interactive Drill
        </h3>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 4, marginBottom: 16 }}>
          An advisory on 'Drip Irrigation Flushing' has been flagged with <strong>🟡 Amber (78%)</strong> confidence due to the technical term 'hydrochloric acid'. Verify the Marathi translation below and approve it.
        </p>

        {/* Simulator */}
        <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
          <div style={{ marginBottom: 12 }}>
            <div className="section-label" style={{ marginBottom: 4 }}>Source (English)</div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>To dissolve the calcium carbonate layer, flush the drip tubes with 0.6% hydrochloric acid at a pressure of 1.5 kg/cm².</p>
          </div>
          <div>
            <div className="section-label" style={{ marginBottom: 4 }}>Translation (Marathi)</div>
            <textarea
              className="text-input"
              value={simEditedText}
              onChange={e => setSimEditedText(e.target.value)}
              rows={3}
              style={{ marginBottom: 0, background: simApproved ? 'rgba(82, 196, 135, 0.1)' : 'var(--bg-surface)' }}
              readOnly={simApproved}
            />
          </div>
        </div>

        <div style={{ marginTop: 12 }}>
          {!simApproved ? (
            <button className="btn btn-sm btn-primary" onClick={() => setSimApproved(true)}>
              ✏️ Save Edit & Approve
            </button>
          ) : (
            <div style={{ fontSize: 12, color: 'var(--green)', fontWeight: 600, background: 'rgba(82, 196, 135, 0.1)', border: '1px solid var(--green)', padding: '8px 12px', borderRadius: 6 }}>
              ✓ Approved! This correction is now permanently stored in the Translation Memory. The system will never make this mistake again.
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h3 onClick={() => setShowReviewRules(s => !s)} style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--text)', cursor: 'pointer' }}>
          {showReviewRules ? '▲' : '▼'}
          💡 Review Protocol Rules
        </h3>
        {showReviewRules && (
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
        )}
      </div>
    </div>
  )
}

const ITAdminTrack = () => (
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
)

const Quiz = () => {
  const [currentQ, setCurrentQ] = useState(0)
  const [selectedOption, setSelectedOption] = useState(null)
  const [score, setScore] = useState(0)
  const [quizFinished, setQuizFinished] = useState(false)
  const [officerName, setOfficerName] = useState('BAIF Field Officer')
  const [certificateToken, setCertificateToken] = useState('')

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
      setCertificateToken(`VAANI-BAIF-${Math.random().toString(36).substring(2, 8).toUpperCase()}`)
      setQuizFinished(true)
    }
  }

  const handleRestartQuiz = () => {
    setCurrentQ(0)
    setSelectedOption(null)
    setScore(0)
    setQuizFinished(false)
    setCertificateToken('')
  }

  return (
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
                  background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, #111C30 100%)',
                  border: '2px solid #F59E0B',
                  borderRadius: 12,
                  padding: 24,
                  marginBottom: 20,
                  textAlign: 'center',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)'
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
                    Token: {certificateToken} · 100% Offline Validated
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
  )
}

const TABS = [
  { id: 'trainer', label: 'Field Advisory Trainer', icon: '👩‍🏫', component: <TrainerTrack /> },
  { id: 'reviewer', label: 'Quality Assurance Reviewer', icon: '🛡️', component: <ReviewerTrack /> },
  { id: 'it', label: 'IT Administrator', icon: '⚙️', component: <ITAdminTrack /> },
  { id: 'quiz', label: 'Practitioner Certification Exam', icon: '🏆', component: <Quiz /> },
];

export default function TrainingHub() {
  const [activeTab, setActiveTab] = useState('trainer')

  return (
    <div style={{ maxWidth: 1080, margin: '0 auto', paddingBottom: 60 }}>
      {/* Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>🎓 VaaniSetu Field Academy <span style={{ color: '#D97706', fontSize: 18, fontWeight: 700 }}>(वाणीसेतु प्रशिक्षण अकादमी)</span></h2>
          <p>Interactive field officer training, offline speech synthesis workflows, and verified BAIF AI practitioner certification</p>
        </div>
      </div>

      {/* 
        Tab selection buttons. 
        Note: The extensive inline styles could be moved to a CSS file or a CSS-in-JS solution for better maintainability.
      */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 24, flexWrap: 'wrap' }}>
        {TABS.map(tab => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1,
                minWidth: 200,
                padding: '16px 20px',
                borderRadius: 14,
                cursor: 'pointer',
                border: isActive ? '2px solid #F59E0B' : '1px solid rgba(255, 255, 255, 0.1)',
                background: isActive ? 'rgba(245, 158, 11, 0.2)' : '#111C30',
                transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                boxShadow: isActive ? '0 6px 20px rgba(245, 158, 11, 0.25)' : '0 2px 6px rgba(0, 0, 0, 0.3)',
                transform: isActive ? 'translateY(-2px)' : 'none',
                textAlign: 'left',
                color: 'inherit'
              }}
            >
              <div style={{ fontSize: 28, marginBottom: 8 }}>{tab.icon}</div>
              <h3 style={{ fontSize: 15, fontWeight: 800, margin: 0, color: '#F8FAFC' }}>
                {tab.label}
              </h3>
            </button>
          )
        })}
      </div>

      {/* Active Tab Content */}
      {TABS.find(tab => tab.id === activeTab)?.component}
    </div>
      )}
