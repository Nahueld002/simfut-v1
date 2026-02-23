import Link from 'next/link';
import { ReactNode } from 'react';

export default function MaintenanceLayout({ children }: { children: ReactNode }) {
    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-gray-900 text-white flex flex-col">
                <div className="p-4 border-b border-gray-800">
                    <h1 className="text-xl font-bold">FutSim Admin</h1>
                    <p className="text-xs text-gray-400">Maintenance Mode</p>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <Link href="/maintenance/teams" className="block px-4 py-2 rounded hover:bg-gray-800 transition-colors">
                        Teams
                    </Link>
                    <Link href="/maintenance/competitions" className="block px-4 py-2 rounded hover:bg-gray-800 transition-colors">
                        Competitions
                    </Link>
                    <Link href="/maintenance/database" className="block px-4 py-2 rounded hover:bg-gray-800 transition-colors text-yellow-400">
                        Database Control
                    </Link>
                    {/* Future modules */}
                    <span className="block px-4 py-2 text-gray-500 cursor-not-allowed">Players (Coming Soon)</span>
                    <span className="block px-4 py-2 text-gray-500 cursor-not-allowed">Matches (Coming Soon)</span>
                </nav>

                <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
                    v0.2.0 - Functional Refresh
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
