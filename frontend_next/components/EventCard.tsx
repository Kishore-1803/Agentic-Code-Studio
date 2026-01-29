import { AgentEvent } from "@/app/page";
import { Code2, AlertCircle, Terminal, Zap, Activity, AlertTriangle, ChevronDown, ChevronUp, CheckCircle2, XCircle, Gauge, ShieldCheck } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { CodeBlock } from "./CodeBlock";
import { useState } from "react";

interface EventCardProps {
    event: AgentEvent;
    originalCode?: string;
}

export function EventCard({ event, originalCode }: EventCardProps) {
    const [showCode, setShowCode] = useState(false);

    const getIcon = () => {
        switch (event.agent.toLowerCase()) {
            case 'developer': return <Code2 className="w-4 h-4" />;
            case 'security engineer': return <ShieldCheck className="w-4 h-4" />;
            case 'critic': return <AlertCircle className="w-4 h-4" />;
            case 'tester': return <Terminal className="w-4 h-4" />;
            case 'optimizer': return <Zap className="w-4 h-4" />;
            case 'benchmarker': return <Gauge className="w-4 h-4" />;
            case 'error': return <AlertTriangle className="w-4 h-4" />;
            default: return <Activity className="w-4 h-4" />;
        }
    };

    const getColors = () => {
        switch (event.agent.toLowerCase()) {
            case 'security engineer': return 'border-orange-500/30 text-orange-400 bg-orange-900/10 shadow-[0_0_10px_rgba(249,115,22,0.1)]';
            case 'developer': return 'border-blue-500/30 text-blue-400 bg-blue-900/10 shadow-[0_0_10px_rgba(37,99,235,0.1)]';
            case 'critic': return 'border-orange-500/30 text-orange-400 bg-orange-900/10 shadow-[0_0_10px_rgba(249,115,22,0.1)]';
            case 'tester': return 'border-green-500/30 text-green-400 bg-green-900/10 shadow-[0_0_10px_rgba(34,197,94,0.1)]';
            case 'optimizer': return 'border-purple-500/30 text-purple-400 bg-purple-900/10 shadow-[0_0_10px_rgba(168,85,247,0.1)]';
            case 'benchmarker': return 'border-cyan-500/30 text-cyan-400 bg-cyan-900/10 shadow-[0_0_10px_rgba(6,182,212,0.1)]';
            case 'error': return 'border-red-500/30 text-red-400 bg-red-900/10 shadow-[0_0_10px_rgba(239,68,68,0.1)]';
            default: return 'border-slate-500/30 text-slate-400 bg-slate-900/10';
        }
    };

    const renderStatusBadge = () => {
        if (!event.metadata?.status) return null;
        
        const status = event.metadata.status.toLowerCase();
        const isSuccess = status === 'approved' || status === 'passed';
        const isFailure = status === 'rejected' || status === 'failed';

        // Only show badge for clear success/failure states
        if (!isSuccess && !isFailure) return null;

        return (
            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider border ${
                isSuccess 
                    ? 'bg-green-500/10 text-green-400 border-green-500/30' 
                    : 'bg-red-500/10 text-red-400 border-red-500/30'
            }`}>
                {isSuccess ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                {event.metadata.status}
            </div>
        );
    };

    const renderBenchmarkStats = () => {
        if (!event.metadata?.stats) return null;
        const stats = event.metadata.stats;

        return (
            <div className="mt-3 grid grid-cols-2 gap-2">
                {Object.entries(stats).map(([key, value]) => (
                    <div key={key} className="bg-black/30 rounded p-2 border border-white/5 flex flex-col">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">
                            {key.replace(/_/g, ' ')}
                        </span>
                        <span className="font-mono text-cyan-400 text-sm">
                            {typeof value === 'number' ? value.toFixed(4) : String(value)}
                        </span>
                    </div>
                ))}
            </div>
        );
    };
const renderVulnerabilities = () => {
        if (!event.metadata?.vulnerabilities || event.metadata.vulnerabilities.length === 0) return null;
        
        return (
            <div className="mt-3 flex flex-col gap-2">
                <div className="text-[10px] text-red-400/80 uppercase tracking-wider font-bold">Detected Vulnerabilities</div>
                {event.metadata.vulnerabilities.map((vuln: any, idx: number) => (
                    <div key={idx} className="bg-red-500/10 border border-red-500/20 rounded p-2 text-xs">
                        <div className="flex items-center justify-between mb-1">
                            <span className="font-bold text-red-400">{vuln.type}</span>
                            <span className="bg-red-500/20 text-red-300 px-1.5 py-0.5 rounded text-[10px] uppercase">{vuln.severity}</span>
                        </div>
                        <p className="text-slate-400">{vuln.description}</p>
                    </div>
                ))}
            </div>
        );
    };

    
    const renderComplexity = () => {
        if (!event.metadata?.complexity) return null;
        
        const { orig_time, orig_space, opt_time, opt_space } = event.metadata.complexity;
        
        return (
            <div className="mt-4 grid grid-cols-2 gap-4 bg-black/20 p-3 rounded border border-white/5">
                <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Time Complexity</div>
                    <div className="flex items-center gap-2">
                        <span className="text-slate-400 line-through text-xs">{orig_time}</span>
                        <span className="text-green-400 font-bold">{opt_time}</span>
                    </div>
                </div>
                <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Space Complexity</div>
                    <div className="flex items-center gap-2">
                        <span className="text-slate-400 line-through text-xs">{orig_space}</span>
                        <span className="text-green-400 font-bold">{opt_space}</span>
                    </div>
                </div>
            </div>
        );
    };

    // Optimization complexity display (for Optimizer and Benchmarker events)
    const agentKey = event.agent.toLowerCase();
    
    return (
        <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`p-4 rounded border-l-2 ${getColors()} border-y border-r border-white/5 font-mono relative overflow-hidden group mb-3`}
        >
            <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
                {renderVulnerabilities()}
                {renderComplexity()}
            <div className="flex items-center justify-between mb-2 relative z-10">
                <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded border ${getColors().split(' ').slice(0, 2).join(' ')} bg-opacity-20`}>
                        {getIcon()}
                    </div>
                    <span className="font-bold uppercase tracking-wider text-xs opacity-90">
                        {event.agent} Node
                    </span>
                    {renderStatusBadge()}
                </div>
                <span className="ml-auto text-[10px] opacity-50 tracking-widest">
                    {new Date().toLocaleTimeString()}
                </span>
            </div>
            <div className="pl-11 relative z-10">
                <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {event.message}
                </p>

                {renderBenchmarkStats()}

                {event.metadata?.code && (
                    <div className="mt-3">
                        <button 
                            onClick={() => setShowCode(!showCode)}
                            className="flex items-center gap-2 text-xs text-slate-400 hover:text-white transition-colors bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded border border-white/5 w-full justify-between"
                        >
                            <span className="flex items-center gap-2">
                                <Code2 className="w-3 h-3" />
                                {showCode ? 'Hide Code Snapshot' : 'View Code Snapshot'}
                            </span>
                            {showCode ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                        <AnimatePresence>
                            {showCode && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="mt-2 border border-white/10 rounded overflow-hidden">
                                        <CodeBlock 
                                            code={event.metadata.code} 
                                            originalCode={originalCode} 
                                            fileName="Snapshot.py"
                                        />
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                )}

                {event.metadata && Object.keys(event.metadata).filter(k => k !== 'code' && k !== 'stats' && k !== 'status').length > 0 && (
                    <div className="mt-3 p-2 bg-black/40 rounded border border-white/5 text-xs font-mono text-slate-500 overflow-x-auto">
                        <div className="flex items-center gap-2 mb-1 text-[10px] uppercase tracking-wider opacity-50">
                            <Activity className="w-3 h-3" /> Payload Data
                        </div>
                        <pre>{JSON.stringify(
                            Object.fromEntries(Object.entries(event.metadata).filter(([k]) => k !== 'code' && k !== 'stats' && k !== 'status')), 
                            null, 
                            2
                        )}</pre>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
