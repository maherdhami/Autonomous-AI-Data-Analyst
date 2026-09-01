import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { AnalysisData, FileMetadata, ChartConfig, ChatMessage } from '@/types';

interface AnalysisState {
  activeFile: FileMetadata | null;
  activeAnalysis: AnalysisData | null;
  history: AnalysisData[];
  apiKey: string;
  
  // 4 Distinct Outputs
  output1: string | null;
  output2: string | null;
  output3: ChartConfig[] | null;
  output4: string | null;
  qualityScore: number | null;
  
  // Chat Memory
  messages: ChatMessage[];
  sessionId: string;

  // Actions
  setActiveFile: (file: FileMetadata | null) => void;
  setActiveAnalysis: (analysis: AnalysisData | null) => void;
  setHistory: (history: AnalysisData[]) => void;
  setApiKey: (key: string) => void;
  
  setOutput1: (content: string | null, score?: number) => void;
  setOutput2: (content: string | null) => void;
  setOutput3: (charts: ChartConfig[] | null) => void;
  setOutput4: (content: string | null) => void;
  
  setMessages: (messages: ChatMessage[] | ((prev: ChatMessage[]) => ChatMessage[])) => void;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  resetOutputs: () => void;
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      activeFile: null,
      activeAnalysis: null,
      history: [],
      apiKey: '',
      
      output1: null,
      output2: null,
      output3: null,
      output4: null,
      qualityScore: null,
      
      messages: [
        {
          role: 'assistant',
          content: 'Hello! I am your Autonomous AI Data Analyst. Ask me strategic business questions or ask me to write Python code to analyze your uploaded dataset.',
          timestamp: Date.now(),
        },
      ],
      sessionId: `ses_${Math.random().toString(36).substring(2, 11)}`,

      setActiveFile: (file) => set({ activeFile: file }),
      setActiveAnalysis: (analysis) => {
        if (analysis) {
          set({
            activeAnalysis: analysis,
            activeFile: analysis.file_metadata,
            output1: analysis.quality_assessment,
            output2: analysis.business_analysis,
            output3: analysis.charts,
            output4: analysis.executive_strategy,
            qualityScore: analysis.quality_score,
          });
        } else {
          set({ activeAnalysis: null });
        }
      },
      setHistory: (history) => set({ history }),
      setApiKey: (apiKey) => set({ apiKey }),

      setOutput1: (content, score) => set((state) => ({ 
        output1: content, 
        qualityScore: score !== undefined ? score : (state.qualityScore || 98) 
      })),
      setOutput2: (content) => set({ output2: content }),
      setOutput3: (charts) => set({ output3: charts }),
      setOutput4: (content) => set({ output4: content }),

      setMessages: (updater) => set((state) => ({
        messages: typeof updater === 'function' ? updater(state.messages) : updater
      })),
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
      })),
      clearMessages: () => set({
        messages: [
          {
            role: 'assistant',
            content: 'Hello! I am your Autonomous AI Data Analyst. Ask me strategic business questions or ask me to write Python code to analyze your uploaded dataset.',
            timestamp: Date.now(),
          },
        ],
        sessionId: `ses_${Math.random().toString(36).substring(2, 11)}`
      }),
      resetOutputs: () => set({
        output1: null,
        output2: null,
        output3: null,
        output4: null,
        qualityScore: null,
      })
    }),
    {
      name: 'ai-data-analyst-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        activeFile: state.activeFile,
        activeAnalysis: state.activeAnalysis,
        apiKey: state.apiKey,
        output1: state.output1,
        output2: state.output2,
        output3: state.output3,
        output4: state.output4,
        qualityScore: state.qualityScore,
        messages: state.messages,
        sessionId: state.sessionId,
      }),
    }
  )
);
