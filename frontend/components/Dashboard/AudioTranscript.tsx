"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import { Play, Pause, StopCircle, Volume2 } from "lucide-react";
import { motion } from "framer-motion";

interface AudioTranscriptProps {
  issues: string[];
  suggestions: string[];
  sentiment?: string;
}

function buildSentences(issues: string[], suggestions: string[], sentiment?: string): string[] {
  const s: string[] = [];
  if (sentiment) {
    s.push(`Overall audience sentiment is ${sentiment.toLowerCase()}.`);
  }
  if (issues.length > 0) {
    s.push(...issues.map((i) => i + "."));
  }
  if (suggestions.length > 0) {
    s.push(...suggestions.map((su) => su + "."));
  }
  return s;
}

export default function AudioTranscript({ issues, suggestions, sentiment }: AudioTranscriptProps) {
  const [state, setState] = useState<"idle" | "playing" | "paused">("idle");
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const sentenceRefs = useRef<(HTMLParagraphElement | null)[]>([]);

  const sentences = buildSentences(issues, suggestions, sentiment);
  const fullText = sentences.join(" ");

  const charRanges = useRef<{ start: number; end: number }[]>([]);
  useEffect(() => {
    let pos = 0;
    charRanges.current = sentences.map((s) => {
      const range = { start: pos, end: pos + s.length };
      pos += s.length + 1;
      return range;
    });
  }, [sentences]);

  const stop = useCallback(() => {
    window.speechSynthesis.cancel();
    setState("idle");
    setActiveIndex(-1);
  }, []);

  const play = useCallback(() => {
    if (state === "paused") {
      window.speechSynthesis.resume();
      setState("playing");
      return;
    }

    const utterance = new SpeechSynthesisUtterance(fullText);
    utterance.rate = 0.85;
    utterance.pitch = 1;

    utterance.onboundary = (e) => {
      if (e.name === "sentence" || e.name === "word") {
        const charIdx = e.charIndex ?? 0;
        const match = charRanges.current.findIndex((r) => charIdx >= r.start && charIdx < r.end);
        if (match !== -1 && match !== activeIndex) {
          setActiveIndex(match);
          sentenceRefs.current[match]?.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }
    };

    utterance.onend = () => {
      setState("idle");
      setActiveIndex(-1);
    };

    utterance.onerror = () => {
      setState("idle");
      setActiveIndex(-1);
    };

    window.speechSynthesis.speak(utterance);
    setState("playing");
    setActiveIndex(0);
  }, [fullText, state, activeIndex]);

  const pause = useCallback(() => {
    window.speechSynthesis.pause();
    setState("paused");
  }, []);

  useEffect(() => () => window.speechSynthesis.cancel(), []);

  if (sentences.length === 0) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px" }}>
        <Volume2 size={16} style={{ opacity: 0.5 }} />
        <span style={{ fontSize: "0.85rem", opacity: 0.6, flex: 1 }}>Audio Narration</span>

        <div style={{ display: "flex", gap: "8px" }}>
          {state === "idle" || state === "paused" ? (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={play}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                background: state === "paused" ? "var(--card-bg)" : "var(--accent)",
                color: state === "paused" ? "var(--foreground)" : "#000",
                border: "1px solid var(--card-border)",
                padding: "8px 16px",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.85rem",
              }}
            >
              <Play size={14} fill={state === "paused" ? "currentColor" : "#000"} />
              {state === "paused" ? "Resume" : "Listen"}
            </motion.button>
          ) : (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={pause}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                background: "var(--card-bg)",
                color: "var(--foreground)",
                border: "1px solid var(--card-border)",
                padding: "8px 16px",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.85rem",
              }}
            >
              <Pause size={14} /> Pause
            </motion.button>
          )}
          {state !== "idle" && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={stop}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                background: "transparent",
                color: "var(--foreground)",
                opacity: 0.6,
                border: "1px solid var(--card-border)",
                padding: "8px 12px",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "0.85rem",
              }}
            >
              <StopCircle size={14} />
            </motion.button>
          )}
        </div>
      </div>

      <div
        ref={containerRef}
        style={{
          maxHeight: "260px",
          overflowY: "auto",
          padding: "16px",
          borderRadius: "10px",
          background: "rgba(0,0,0,0.2)",
          border: "1px solid var(--card-border)",
        }}
      >
        {sentences.map((sentence, i) => (
          <p
            key={i}
            ref={(el) => { sentenceRefs.current[i] = el; }}
            style={{
              margin: "0 0 8px 0",
              padding: "6px 10px",
              borderRadius: "6px",
              lineHeight: "1.6",
              fontSize: "0.95rem",
              color: activeIndex === i ? "var(--foreground)" : activeIndex > -1 ? "rgba(255,255,255,0.3)" : "rgba(255,255,255,0.65)",
              background: activeIndex === i ? "rgba(34, 211, 238, 0.1)" : "transparent",
              borderLeft: activeIndex === i ? "2px solid var(--accent)" : "2px solid transparent",
              transition: "all 0.15s ease",
            }}
          >
            {activeIndex === i ? (
              <>
                {sentence}{" "}
                <span
                  style={{
                    display: "inline-block",
                    width: "6px",
                    height: "14px",
                    background: "var(--accent)",
                    animation: "blink 0.6s step-end infinite",
                    verticalAlign: "middle",
                    marginLeft: "2px",
                  }}
                />
              </>
            ) : (
              sentence
            )}
          </p>
        ))}
      </div>

      <style>{`
        @keyframes blink {
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
