import { Code2, AlertCircle, TestTube2, Play, Loader2, ShieldCheck } from "lucide-react";
import { clsx } from "clsx";
import { useEffect } from "react";

interface SidebarProps {
    mode: "fix" | "optimize" | "security";
    inputCode: string;
    setInputCode: (code: string) => void;
    bugDescription: string;
    setBugDescription: (desc: string) => void;
    testInput: string;
    setTestInput: (input: string) => void;
    startProcess: () => void;
    processing: boolean;
    language: "python" | "cpp" | "java" | "javascript";
    setLanguage: (lang: "python" | "cpp" | "java" | "javascript") => void;
    complexityData?: {
        origTime?: string;
        origSpace?: string;
        optTime?: string;
        optSpace?: string;
    };
}

export function Sidebar({
    mode,
    inputCode,
    setInputCode,
    bugDescription,
    setBugDescription,
    testInput,
    setTestInput,
    startProcess,
    processing,
    language,
    setLanguage,
    complexityData
}: SidebarProps) {
    
    useEffect(() => {
        // Just rely on initial state or user selection, don't force SQL since we are fixing Python wrappers usually
        if (mode === 'security') {
            // Optional: reset to python if we want security to imply python backend issues
        }
    }, [mode, setLanguage]);

    return (
        <div className="flex-1 p-6 flex flex-col gap-6 hud-panel rounded-xl overflow-y-auto h-full">
            <div className="absolute top-0 right-0 px-4 py-1 bg-blue-500/10 border-b border-l border-blue-500/30 text-[10px] font-mono text-blue-400 uppercase tracking-widest">
                Input Module
            </div>

            <div className="flex flex-col gap-2 mt-4">
                <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-2">
                        <Code2 className="w-4 h-4" /> Source Code
                    </label>
                    <select 
                        value={language}
                        onChange={(e) => {
                            console.log("Language changed to:", e.target.value);
                            setLanguage(e.target.value as any);
                        }}
                        disabled={mode === 'security'}
                        className={clsx(
                            "bg-blue-950/50 border border-blue-500/30 text-blue-300 text-[10px] rounded px-2 py-1 uppercase font-mono focus:outline-none focus:border-blue-500",
                            mode === 'security' && "opacity-50 cursor-not-allowed"
                        )}
                    >
                        {mode === 'security' ? (
                            <option value="python">Python (SQL)</option>
                        ) : (
                            <>
                                <option value="python">Python</option>
                                <option value="javascript">JavaScript</option>
                                <option value="cpp">C++</option>
                                <option value="java">Java</option>
                            </>
                        )}
                    </select>
                </div>
                <div className="relative group transition-all duration-300 focus-within:ring-1 focus-within:ring-blue-500/50 rounded-lg bg-black/40 border border-blue-500/20">
                    <textarea 
                        value={inputCode}
                        onChange={(e) => setInputCode(e.target.value)}
                        className="w-full h-64 bg-transparent border-none rounded-lg p-4 font-mono text-sm focus:ring-0 transition-all resize-none text-blue-100 placeholder:text-blue-900/50"
                        placeholder="Paste your code here..."
                    />
                    <div className="absolute bottom-2 right-2 text-[10px] text-blue-500 font-mono px-2 py-0.5 rounded border border-blue-500/30 bg-blue-900/10 uppercase">{language}</div>
                </div>
            </div>

            {mode === 'fix' && (
                <div className="flex flex-col gap-2">
                    <label className="text-xs font-bold text-red-400 uppercase tracking-wider flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" /> Bug Report
                    </label>
                    <div className="relative group transition-all duration-300 focus-within:ring-1 focus-within:ring-red-500/50 rounded-lg bg-black/40 border border-red-500/20">
                        <textarea 
                            value={bugDescription}
                            onChange={(e) => setBugDescription(e.target.value)}
                            className="w-full h-32 bg-transparent border-none rounded-lg p-4 text-sm focus:ring-0 transition-all resize-none text-red-100 placeholder:text-red-900/50 font-mono"
                            placeholder="Describe the anomaly..."
                        />
                    </div>
                </div>
            )}

            {mode === 'optimize' && (
                <div className="flex flex-col gap-2">
                    <label className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                        <TestTube2 className="w-4 h-4" /> Test Vector
                    </label>
                    <div className="relative group transition-all duration-300 focus-within:ring-1 focus-within:ring-purple-500/50 rounded-lg bg-black/40 border border-purple-500/20">
                        <textarea 
                            value={testInput}
                            onChange={(e) => setTestInput(e.target.value)}
                            className="w-full h-32 bg-transparent border-none rounded-lg p-4 font-mono text-sm focus:ring-0 transition-all resize-none text-purple-100 placeholder:text-purple-900/50"
                            placeholder="Input data for optimization..."
                        />
                    </div>
                    
                    {/* Complexity Card */}
                    {complexityData && (complexityData.origTime || complexityData.optTime) && (
                        <div className="mt-4 rounded-lg border border-blue-700/40 bg-blue-950/40 px-6 py-4 flex flex-col gap-3 shadow-lg backdrop-blur-sm">
                            <div className="flex gap-8 justify-around">
                                <div className="flex flex-col items-center">
                                    <div className="text-[10px] uppercase text-blue-400 font-bold tracking-widest mb-2">Time Complexity</div>
                                    <div className="flex items-center gap-3 text-sm">
                                        <span className="text-slate-300 font-mono bg-black/30 px-2 py-1 rounded border border-white/5">{complexityData.origTime || '?'}</span>
                                        <span className="text-blue-500 font-bold">→</span>
                                        <span className="text-green-400 font-mono bg-green-900/20 px-2 py-1 rounded border border-green-500/30 shadow-[0_0_10px_rgba(74,222,128,0.1)]">{complexityData.optTime || '?'}</span>
                                    </div>
                                </div>
                                <div className="w-px bg-blue-500/20"></div>
                                <div className="flex flex-col items-center">
                                    <div className="text-[10px] uppercase text-blue-400 font-bold tracking-widest mb-2">Space Complexity</div>
                                    <div className="flex items-center gap-3 text-sm">
                                        <span className="text-slate-300 font-mono bg-black/30 px-2 py-1 rounded border border-white/5">{complexityData.origSpace || '?'}</span>
                                        <span className="text-blue-500 font-bold">→</span>
                                        <span className="text-green-400 font-mono bg-green-900/20 px-2 py-1 rounded border border-green-500/30 shadow-[0_0_10px_rgba(74,222,128,0.1)]">{complexityData.optSpace || '?'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            <button 
                onClick={startProcess}
                disabled={processing}
                className={clsx(
                    'mt-auto py-4 rounded-lg font-bold text-white shadow-[0_0_20px_rgba(0,0,0,0.5)] flex items-center justify-center gap-2 transition-all duration-300 transform hover:scale-[1.01] active:scale-[0.99] relative overflow-hidden group border', 
                    processing ? 'bg-slate-800 border-slate-700 cursor-not-allowed text-slate-500' : (
                        mode === 'fix' ? 'bg-blue-600/20 border-blue-500 hover:bg-blue-600/30 hover:shadow-[0_0_30px_rgba(37,99,235,0.3)]' :
                        mode === 'optimize' ? 'bg-purple-600/20 border-purple-500 hover:bg-purple-600/30 hover:shadow-[0_0_30px_rgba(147,51,234,0.3)]' :
                        'bg-orange-600/20 border-orange-500 hover:bg-orange-600/30 hover:shadow-[0_0_30px_rgba(249,115,22,0.3)]'
                    )
                )}
            >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                {!processing ? (
                    <>
                        {mode === 'security' ? <ShieldCheck className="w-5 h-5 relative z-10" /> : <Play className="w-5 h-5 relative z-10" />}
                        <span className="relative z-10 font-mono tracking-widest uppercase">
                            {mode === 'fix' ? 'Initiate Debug Protocol' : 
                             mode === 'optimize' ? 'Initiate Optimization' : 'Initiate Security Audit'}
                        </span>
                    </>
                ) : (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin relative z-10" /> <span className="relative z-10 font-mono tracking-widest uppercase">Processing...</span>
                    </>
                )}
            </button>
        </div>
    );
}
