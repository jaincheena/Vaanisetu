import React, { useState } from 'react'

const QUIZ_QUESTIONS = [
  {
    id: 1,
    level: "Level 1: AgriShield™ & Domain Safety",
    question: "A training video mentions 'PM-KISAN', 'DAP', and 'Gir cattle'. How does VaaniSetu prevent these mission-critical terms from being corrupted by translation?",
    options: [
      { text: "It relies on Google Translate cloud dictionary", correct: false, explain: "VaaniSetu runs 100% offline with zero cloud dependency." },
      { text: "AgriShield™ wraps 120+ domain entities in protected tokens (<VSPn>) before translation and restores them verbatim", correct: true, explain: "Correct! AgriShield™ uses token shields to ensure critical schemes, pests, and chemical names are never mistranslated." },
      { text: "It translates every word literally into Sanskrit", correct: false, explain: "Literal translation of schemes causes dangerous confusion in rural advisory." },
      { text: "It asks the user to manually re-type every acronym", correct: false, explain: "AgriShield™ performs automated regex entity preservation." }
    ]
  },
  {
    id: 2,
    level: "Level 2: The Quality Gatekeeper",
    question: "A translated advisory on 'Propiconazole dosage for Yellow Rust' receives an AI confidence score of 0.71 (🟡 Amber). What is the mandatory protocol?",
    options: [
      { text: "Immediately forward the video to farmer WhatsApp groups", correct: false, explain: "Never share Amber content before review; incorrect chemical dosages can harm crops." },
      { text: "Check the Review Queue, verify/edit the Marathi translation, and approve it to clear distribution and train Translation Memory", correct: true, explain: "Spot on! Approving the correction in the Review Queue clears the job for distribution and permanently updates SQLite Translation Memory." },
      { text: "Delete the entire video and record it again", correct: false, explain: "No need to re-record; simply edit the single flagged sentence in the web UI." },
      { text: "Ignore the amber badge because AI is always accurate", correct: false, explain: "The Confidence Gate is specifically designed to prevent unverified distribution." }
    ]
  },
  {
    id: 3,
    level: "Level 3: Last-Mile Delivery Architecture",
    question: "A BAIF field officer in tribal Nandurbar is reaching farmers who only own ₹1,000 basic feature phones with no internet. Which output format should be dispatched?",
    options: [
      { text: "1080p Full HD Subtitled MP4", correct: false, explain: "Basic feature phones cannot play high-definition video or read subtitles." },
      { text: "8kHz Mono IVR Audio (.wav) for direct telecom broadcast", correct: true, explain: "Exactly! VaaniSetu auto-generates 8kHz mono audio optimized for GSM voice broadcasts on basic keypad phones." },
      { text: "Large 45MB PDF Document", correct: false, explain: "Requires smartphone document viewers and high literacy." },
      { text: "Raw JSON subtitle timing manifest", correct: false, explain: "Manifests are internal machine formats." }
    ]
  },
  {
    id: 4,
    level: "Level 4: Hardware & RAM Concurrency",
    question: "Two training officers upload large videos simultaneously on an 8GB RAM field laptop. How does VaaniSetu ensure the laptop doesn't freeze or crash?",
    options: [
      { text: "It connects to Amazon Web Services to offload compute", correct: false, explain: "VaaniSetu is strictly 100% offline." },
      { text: "The RAM-Aware Concurrency Planner throttles workers, protects memory headroom, and serializes heavy stages with mutex locks", correct: true, explain: "Bravo! The dynamic resource planner monitors available memory and serializes Whisper/TTS inference to prevent OOM swapping." },
      { text: "It forcefully closes all other running programs", correct: false, explain: "VaaniSetu peacefully respects OS memory headroom." },
      { text: "It randomly deletes the second video", correct: false, explain: "Jobs are safely enqueued in SQLite WAL mode." }
    ]
  }
]

const STORYBOARDS = [
  {
    title: "⚡ 60-Sec Quickstart: Localizing a Broadcast in 3 Clicks",
    steps: [
      "1. Open http://localhost:8765 on office WiFi",
      "2. Click '🌾 Scenario 1: Crop Disease' preset (or drag your MP4/DOCX)",
      "3. Select target languages (Marathi, Hindi) & click 'Start AI Localization'",
      "4. Listen to the synthetic audio in the In-Browser Studio & download the ZIP"
    ]
  },
  {
    title: "🛡️ 60-Sec Quality Control: Clearing the Review Queue",
    steps: [
      "1. Notice the yellow badge 'Review Needed' on newly completed jobs",
      "2. Navigate to 'Review Queue' in the sidebar",
      "3. Review the side-by-side original vs translated agricultural sentence",
      "4. Click 'Approve' or make a quick edit -> Translation Memory is instantly updated!"
    ]
  },
  {
    title: "📞 60-Sec Last Mile: Delivering to Basic Keypad Phones",
    steps: [
      "1. Select 'IVR .wav' in the upload output format selector",
      "2. When complete, navigate to the 'Feature Phone IVR' tab in the Result Studio",
      "3. Test the 8kHz telecom audio playback directly in the dialer mockup",
      "4. Export the .wav file to BAIF's bulk outbound voice call server"
    ]
  }
]

export default function TrainingHub() {
  const [selectedTrack, setSelectedTrack] = useState('trainer')
  const [currentQ, setCurrentQ] = useState(0)
  const [selectedOption, setSelectedOption] = useState(null)
  const [score, setScore] = useState(0)
  const [quizFinished, setQuizFinished] = useState(false)
  const [userName, setUserName] = useState('BAIF Field Officer')

  const handleSelectOption = (idx) => {
    if (selectedOption !== null) return
    setSelectedOption(idx)
    if (QUIZ_QUESTIONS[currentQ].options[idx].correct) {
      setScore(prev => prev + 1)
    }
  }

  const handleNext = () => {
    if (currentQ < QUIZ_QUESTIONS.length - 1) {
      setCurrentQ(prev => prev + 1)
      setSelectedOption(null)
    } else {
      setQuizFinished(true)
    }
  }

  const handleRestart = () => {
    setCurrentQ(0)
    setSelectedOption(null)
    setScore(0)
    setQuizFinished(false)
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <span style={{ fontSize: 32 }}>🎓</span>
          <h1 style={{ fontSize: 26, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
            Interactive Handover & Gamified Training Academy
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14, margin: 0 }}>
          Interactive mastery tracks, scenario quizzes, and micro-learning storyboards for BAIF field officers, content reviewers, and IT administrators.
        </p>
      </div>

      {/* Role Tracks */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, marginBottom: 32 }}>
        <div 
          onClick={() => setSelectedTrack('trainer')}
          style={{
            padding: 20,
            borderRadius: 12,
            border: selectedTrack === 'trainer' ? '2px solid var(--accent-green)' : '1px solid var(--border)',
            background: selectedTrack === 'trainer' ? 'rgba(34, 197, 94, 0.08)' : 'var(--bg-card)',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <div style={{ fontSize: 24, marginBottom: 8 }}>🌾 Field Trainer Track</div>
          <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 6px 0' }}>Training & Extension Officers</h3>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
            Master 1-click presets, microphone voice recording, and multi-format farmer distribution.
          </p>
        </div>

        <div 
          onClick={() => setSelectedTrack('reviewer')}
          style={{
            padding: 20,
            borderRadius: 12,
            border: selectedTrack === 'reviewer' ? '2px solid var(--accent-green)' : '1px solid var(--border)',
            background: selectedTrack === 'reviewer' ? 'rgba(34, 197, 94, 0.08)' : 'var(--bg-card)',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <div style={{ fontSize: 24, marginBottom: 8 }}>🛡️ Quality Gatekeeper Track</div>
          <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 6px 0' }}>Bilingual Content Reviewers</h3>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
            Learn the Confidence Gate, Review Queue approval, and Translation Memory compounding.
          </p>
        </div>

        <div 
          onClick={() => setSelectedTrack('it')}
          style={{
            padding: 20,
            borderRadius: 12,
            border: selectedTrack === 'it' ? '2px solid var(--accent-green)' : '1px solid var(--border)',
            background: selectedTrack === 'it' ? 'rgba(34, 197, 94, 0.08)' : 'var(--bg-card)',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <div style={{ fontSize: 24, marginBottom: 8 }}>⚙️ IT & Operations Track</div>
          <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 6px 0' }}>Systems & Regional Admins</h3>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
            Master air-gapped deployment, automated backups, rollback procedures, and resource sizing.
          </p>
        </div>
      </div>

      {/* Main Grid: Quiz & Storyboards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 24 }}>
        {/* Left: Gamified Certification Quiz */}
        <div style={{ background: 'var(--bg-card)', padding: 24, borderRadius: 16, border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-green)', letterSpacing: '0.05em' }}>
              🎯 Live Certification Quiz
            </span>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>
              Question {currentQ + 1} of {QUIZ_QUESTIONS.length}
            </span>
          </div>

          {!quizFinished ? (
            <div>
              <div style={{ fontSize: 12, color: 'var(--accent-blue)', fontWeight: 600, marginBottom: 6 }}>
                {QUIZ_QUESTIONS[currentQ].level}
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 20, lineHeight: 1.4 }}>
                {QUIZ_QUESTIONS[currentQ].question}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
                {QUIZ_QUESTIONS[currentQ].options.map((opt, idx) => {
                  let bg = 'var(--bg-primary)'
                  let border = '1px solid var(--border)'
                  let icon = ''
                  if (selectedOption !== null) {
                    if (opt.correct) {
                      bg = 'rgba(34, 197, 94, 0.15)'
                      border = '1px solid var(--accent-green)'
                      icon = '✅ '
                    } else if (selectedOption === idx) {
                      bg = 'rgba(239, 68, 68, 0.15)'
                      border = '1px solid var(--red)'
                      icon = '❌ '
                    }
                  }

                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectOption(idx)}
                      style={{
                        padding: '12px 16px',
                        borderRadius: 10,
                        textAlign: 'left',
                        background: bg,
                        border: border,
                        color: 'var(--text-primary)',
                        fontSize: 13,
                        cursor: selectedOption === null ? 'pointer' : 'default',
                        transition: 'all 0.15s',
                        lineHeight: 1.4
                      }}
                    >
                      <strong>{String.fromCharCode(65 + idx)}.</strong> {icon}{opt.text}
                    </button>
                  )
                })}
              </div>

              {selectedOption !== null && (
                <div style={{ 
                  padding: 12, 
                  borderRadius: 8, 
                  background: QUIZ_QUESTIONS[currentQ].options[selectedOption].correct ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
                  border: '1px solid var(--border)',
                  marginBottom: 16,
                  fontSize: 13,
                  color: 'var(--text-primary)'
                }}>
                  💡 <strong>Explanation:</strong> {QUIZ_QUESTIONS[currentQ].options[selectedOption].explain}
                </div>
              )}

              <button
                disabled={selectedOption === null}
                onClick={handleNext}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: 10,
                  border: 'none',
                  background: selectedOption === null ? 'var(--border)' : 'var(--accent-green)',
                  color: '#fff',
                  fontWeight: 600,
                  fontSize: 14,
                  cursor: selectedOption === null ? 'not-allowed' : 'pointer'
                }}
              >
                {currentQ < QUIZ_QUESTIONS.length - 1 ? 'Next Scenario ➔' : 'Complete Certification 🏆'}
              </button>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '16px 0' }}>
              <div style={{ fontSize: 48, marginBottom: 8 }}>🏆</div>
              <h2 style={{ fontSize: 20, fontWeight: 700, margin: '0 0 6px 0', color: 'var(--text-primary)' }}>
                Certification Exam Completed!
              </h2>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 20 }}>
                Score: <strong>{score} / {QUIZ_QUESTIONS.length}</strong> ({Math.round((score / QUIZ_QUESTIONS.length) * 100)}%)
              </p>

              {/* Certificate Badge */}
              <div style={{
                background: 'linear-gradient(135deg, rgba(34,197,94,0.1), rgba(59,130,246,0.1))',
                border: '2px solid var(--accent-green)',
                borderRadius: 12,
                padding: 20,
                marginBottom: 20,
                textAlign: 'center'
              }}>
                <div style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--accent-green)', fontWeight: 700 }}>
                  BAIF Development Research Foundation
                </div>
                <h3 style={{ fontSize: 18, fontWeight: 700, margin: '8px 0', color: 'var(--text-primary)' }}>
                  Certified AI Localization Practitioner
                </h3>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '0 0 12px 0' }}>
                  Awarded to: <strong>{userName}</strong>
                </p>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Verification Token: VAANI-CERT-{Math.random().toString(36).substring(2, 9).toUpperCase()} · 100% Offline Verified
                </div>
              </div>

              <div style={{ display: 'flex', gap: 10 }}>
                <button
                  onClick={handleRestart}
                  style={{
                    flex: 1,
                    padding: 10,
                    borderRadius: 8,
                    border: '1px solid var(--border)',
                    background: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    fontSize: 13
                  }}
                >
                  🔄 Retake Exam
                </button>
                <button
                  onClick={() => alert(`Certificate successfully stamped for ${userName}!`)}
                  style={{
                    flex: 1,
                    padding: 10,
                    borderRadius: 8,
                    border: 'none',
                    background: 'var(--accent-green)',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                    fontSize: 13
                  }}
                >
                  🖨️ Print Certificate
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Micro-Learning Storyboards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>🎬</span> Micro-Learning Video Storyboards
          </div>

          {STORYBOARDS.map((sb, idx) => (
            <div 
              key={idx} 
              style={{
                background: 'var(--bg-card)',
                padding: 18,
                borderRadius: 12,
                border: '1px solid var(--border)'
              }}
            >
              <h4 style={{ fontSize: 14, fontWeight: 600, margin: '0 0 10px 0', color: 'var(--accent-green)' }}>
                {sb.title}
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {sb.steps.map((step, sIdx) => (
                  <div key={sIdx} style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {step}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Quick Support / Runbook Box */}
          <div style={{
            background: 'rgba(59, 130, 246, 0.08)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: 12,
            padding: 16
          }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent-blue)', marginBottom: 6 }}>
              📞 24/7 Field Operational Runbook
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              • <strong>Server unresponsive?</strong> Run <code>scripts\health_check.bat</code><br />
              • <strong>Corrupted state?</strong> Run <code>scripts\rollback.bat</code><br />
              • <strong>Disk full?</strong> Workspace auto-purges; check <code>C:\VaaniSetu\outputs\</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
