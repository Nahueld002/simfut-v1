'use client';

import { useState } from 'react';
import axios from 'axios';

// Assuming we want to use the same layout as maintenance/teams, we don't need Sidebar here.
// The layout.tsx provided wrapper handles sidebar.

const api = axios.create({ baseURL: 'http://localhost:8000/api/v1' });

export default function DatabasePage() {
    const [logs, setLogs] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Newest logs at top
    const addLog = (msg: string) => setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);

    const runCommand = async (endpoint: string, name: string) => {
        if (isLoading) return;
        setIsLoading(true);
        addLog(`Starting: ${name}...`);
        try {
            const res = await api.post(endpoint);
            // Handle newline logs
            const lines = res.data.message.split('\n');
            lines.forEach((l: string) => addLog(l));
        } catch (err: any) {
            const detail = err.response?.data?.detail || err.message;
            addLog(`ERROR: ${detail}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleExport = () => {
        if (isLoading) return;
        setIsLoading(true);
        addLog("Generating XLSX file on server...");

        // Native browser download (GET request)
        const url = "http://localhost:8000/api/v1/admin/export";
        window.location.href = url;

        setTimeout(() => {
            setIsLoading(false);
            addLog("Export request sent. Check downloads.");
        }, 1000);
    };

    const [importFile, setImportFile] = useState<File | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setImportFile(e.target.files[0]);
        }
    };

    const handleImport = async () => {
        if (!importFile || isLoading) return;
        setIsLoading(true);
        addLog(`Uploading & Importing: ${importFile.name}...`);

        const formData = new FormData();
        formData.append('file', importFile);

        try {
            const res = await api.post('/admin/import', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const lines = res.data.message.split('\n');
            lines.forEach((l: string) => addLog(l));
        } catch (err: any) {
            const detail = err.response?.data?.detail || err.message;
            addLog(`ERROR: ${detail}`);
        } finally {
            setIsLoading(false);
            setImportFile(null);
            // reset file input value? Hard without ref, but okay for now.
        }
    };

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">Database Management</h1>

            {/* 1. Control Panel */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Actions */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                    <h3 className="font-bold text-gray-700 dark:text-gray-200 mb-4 border-b pb-2">Actions</h3>
                    <div className="space-y-3">
                        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900 rounded">
                            <p className="text-sm text-red-600 dark:text-red-400 mb-2 font-bold">Destructive Zone</p>
                            <button
                                onClick={() => {
                                    if (confirm('ARE YOU SURE? THIS WILL WIPE ALL DATA.')) {
                                        runCommand('/admin/reset', 'Full Reset');
                                    }
                                }}
                                disabled={isLoading}
                                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50"
                            >
                                FACTORY RESET (WIPE DB)
                            </button>
                        </div>

                        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900 rounded">
                            <p className="text-sm text-gray-600 dark:text-gray-300 mb-2 font-bold">Seed Data</p>
                            <div className="grid grid-cols-2 gap-2">
                                <button
                                    onClick={() => runCommand('/admin/seed/basic', 'Seed Basic')}
                                    disabled={isLoading}
                                    className="bg-blue-600 hover:bg-blue-700 text-white py-1 px-3 rounded text-sm disabled:opacity-50"
                                >
                                    Seed Basic (Lookups)
                                </button>
                                <button
                                    onClick={() => runCommand('/admin/seed/full', 'Seed Full')}
                                    disabled={isLoading}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white py-1 px-3 rounded text-sm disabled:opacity-50"
                                >
                                    Seed Full (Mock Data)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Import / Export */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                    <h3 className="font-bold text-gray-700 dark:text-gray-200 mb-4 border-b pb-2">Data Transfer</h3>

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Export</label>
                        <button
                            onClick={handleExport}
                            disabled={isLoading}
                            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            Download Full Dataset (.xlsx)
                        </button>
                    </div>

                    <div className="border-t pt-4">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Import</label>
                        <div className="flex gap-2">
                            <input
                                type="file"
                                accept=".xlsx"
                                onChange={handleFileChange}
                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-200"
                            />
                            <button
                                onClick={handleImport}
                                disabled={!importFile || isLoading}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                            >
                                Upload
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Select logic_v2_full.xlsx to restore data.</p>
                    </div>
                </div>
            </div>

            {/* 2. Console Logs */}
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-96 overflow-y-auto border border-gray-700 shadow-inner">
                <div className="flex justify-between items-center mb-2 border-b border-gray-700 pb-1">
                    <span className="font-bold text-gray-300">System Console</span>
                    <button onClick={() => setLogs([])} className="text-xs text-gray-500 hover:text-gray-300">Clear</button>
                </div>
                {logs.length === 0 && <span className="text-gray-600 italic">Ready for commands...</span>}
                {logs.map((log, i) => (
                    <div key={i} className="whitespace-pre-wrap">{log}</div>
                ))}
            </div>
        </div>
    );
}
