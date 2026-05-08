import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './index.css';

type Message = {
  node: string;
  sender: string;
  message: string;
  turn: number;
};

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState<"live" | "history">("live");
  
  // Live State
  const [goal, setGoal] = useState("Design a scalable event-driven architecture for a global fintech application handling 1M RPS.");
  const [mode, setMode] = useState("socratic");
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<"idle" | "running" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  
  // History State
  const [historyList, setHistoryList] = useState<string[]>([]);
  const [selectedTranscript, setSelectedTranscript] = useState<string | null>(null);

  const arenaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (activeTab === "live" && arenaRef.current) {
      arenaRef.current.scrollTop = arenaRef.current.scrollHeight;
    }
  }, [messages, activeTab]);

  const fetchHistoryList = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`);
      const data = await res.json();
      setHistoryList(data.transcripts);
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  const loadTranscript = async (filename: string) => {
    try {
      const res = await fetch(`${API_BASE}/history/${filename}`);
      const data = await res.json();
      setSelectedTranscript(data.content);
    } catch (e) {
      console.error("Failed to load transcript", e);
    }
  };

  const startDebate = async () => {
    setActiveTab("live");
    setMessages([]);
    setStatus("running");
    setErrorMsg("");

    try {
      // 1. Init
      const res = await fetch(`${API_BASE}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ global_goal: goal, mode })
      });
      
      if (!res.ok) throw new Error("Failed to initialize conversation on server.");

      // 2. Stream
      const eventSource = new EventSource(`${API_BASE}/stream`);

      eventSource.addEventListener("message", (e) => {
        const payload = JSON.parse(e.data);
        setMessages(prev => [...prev, payload]);
      });

      eventSource.addEventListener("done", () => {
        setStatus("idle");
        eventSource.close();
      });

      eventSource.addEventListener("error", (e: any) => {
        try {
            if(e.data) {
                const payload = JSON.parse(e.data);
                setErrorMsg(payload.message || "Connection Error");
            }
        } catch(err) {
            setErrorMsg("Stream disconnected unexpectedly.");
        }
        setStatus("error");
        eventSource.close();
      });

    } catch (e: any) {
      setStatus("error");
      setErrorMsg(e.message);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="brand">Dual-Agent Synthetic Dialogue (DASD)</div>
        
        <div className="tabs">
          <button 
            className={activeTab === 'live' ? 'active' : ''}
            onClick={() => setActiveTab("live")}
          >
            Live Arena
          </button>
          <button 
            className={activeTab === 'history' ? 'active' : ''}
            onClick={() => { setActiveTab("history"); fetchHistoryList(); }}
          >
            History
          </button>
        </div>

        {activeTab === "live" ? (
          <>
            <div className="form-group">
              <label>Global Goal</label>
              <textarea 
                rows={5} 
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                disabled={status === "running"}
              />
            </div>

            <div className="form-group">
              <label>Interaction Mode</label>
              <select value={mode} onChange={(e) => setMode(e.target.value)} disabled={status === "running"}>
                <option value="socratic">Socratic Debate</option>
                <option value="blue_sky">Blue-Sky Design</option>
                <option value="stress_test">Stress Test</option>
              </select>
            </div>

            <button 
              className="btn-start" 
              onClick={startDebate} 
              disabled={status === "running"}
            >
              {status === "running" ? "Synthesis in Progress..." : "Initialize Loop"}
            </button>

            <div className="status-indicator">
              <div className={`pulse ${status}`}></div>
              <span>
                {status === "idle" && "Ready to initialize."}
                {status === "running" && "LangGraph Event Stream active..."}
                {status === "error" && `Error: ${errorMsg}`}
              </span>
            </div>
          </>
        ) : (
          <div className="history-list">
            <label>Past Transcripts</label>
            {historyList.length === 0 && <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No transcripts found.</div>}
            {historyList.map((file, idx) => (
              <div 
                key={idx} 
                className="history-item"
                onClick={() => loadTranscript(file)}
              >
                {file}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="arena" ref={arenaRef}>
        {activeTab === "live" ? (
          <>
            <div className="arena-header">
              <h1>Active Synthesis</h1>
              <p>Monitoring LangGraph execution pipeline.</p>
            </div>
            
            <div className="arena-content">
              {messages.length === 0 && status === "idle" && (
                <div style={{ margin: "5rem auto", color: "var(--text-secondary)", textAlign: "center" }}>
                  <h2>Awaiting Sequence</h2>
                  <p style={{ marginTop: "1rem" }}>Initialize the loop to begin multi-agent synthesis.</p>
                </div>
              )}
              
              {messages.map((m, idx) => (
                <div key={idx} className={`message-card ${m.sender}`}>
                  <div className="message-header">
                    <div className="sender-info">
                      <div className="sender-avatar">{m.sender.charAt(0).toUpperCase()}</div>
                      <span className="sender-name">{m.sender}</span>
                    </div>
                    <span className="turn-badge">Turn {m.turn}</span>
                  </div>
                  <div className="message-body">{m.message}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <div className="arena-header">
              <h1>Transcript Archive</h1>
              <p>Viewing historical agent synthesis.</p>
            </div>
            
            <div className="arena-content">
              <div style={{ padding: '2rem', background: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                {selectedTranscript ? (
                  <div className="markdown-body" style={{ color: '#EAEAEA' }}>
                    <ReactMarkdown>{selectedTranscript}</ReactMarkdown>
                  </div>
                ) : (
                  <div style={{ color: "var(--text-secondary)", textAlign: "center", marginTop: '5rem' }}>
                    Select a transcript from the sidebar to view history.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
