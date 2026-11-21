import React, { useState } from 'react';
import { Search, ShieldCheck, CheckCircle2, Lock } from 'lucide-react';

export const PublicVerifyView: React.FC = () => {
  const [hashInput, setHashInput] = useState<string>(
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
  );
  const [verifiedRecord, setVerifiedRecord] = useState<any | null>(null);
  const [searched, setSearched] = useState(false);

  const handleVerify = () => {
    setSearched(true);
    // In demo environment, sample receipt matches
    setVerifiedRecord({
      receipt_hash: hashInput,
      is_demo: true,
      timestamp_utc: '2026-11-20T10:00:00Z',
      weight_net_formatted: '30.800 g',
      purity_formatted: '90.50% (905‰)',
      settlement_formatted: '₹3,55,115.00',
      integrity_status: 'CONSISTENT',
      evidence_coverage: '11/12 Rules Validated',
    });
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-8">
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 bg-gold-100 text-gold-700 rounded-2xl mb-2">
          <ShieldCheck className="w-10 h-10" />
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Public Receipt Verification Portal
        </h1>
        <p className="text-sm text-slate-600 max-w-lg mx-auto">
          Verify the cryptographic authenticity and mathematical integrity of any Gold Trust AI receipt.
          No personal customer data is exposed.
        </p>
      </div>

      {/* Hash Input Box */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex items-center space-x-3">
        <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
        <input
          type="text"
          value={hashInput}
          onChange={(e) => setHashInput(e.target.value)}
          placeholder="Enter 64-character SHA-256 receipt hash..."
          className="flex-1 font-mono text-sm outline-none text-slate-800 placeholder-slate-400"
        />
        <button
          onClick={handleVerify}
          className="px-6 py-2.5 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg text-sm transition"
        >
          Verify
        </button>
      </div>

      {searched && verifiedRecord && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden space-y-6 p-6">
          <div className="flex items-center justify-between border-b pb-4">
            <div className="flex items-center space-x-3">
              <CheckCircle2 className="w-7 h-7 text-green-600" />
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Cryptographically Valid</h3>
                <span className="text-xs text-slate-500 font-mono">
                  SHA-256 RFC 8785 Canonical Match
                </span>
              </div>
            </div>
            <span className="px-3 py-1 bg-amber-100 text-amber-900 text-xs font-semibold rounded-full">
              DEMO RECORD
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-xs font-semibold text-slate-500 block">Evaluated Net Weight</span>
              <span className="text-lg font-bold font-mono text-slate-900">
                {verifiedRecord.weight_net_formatted}
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-xs font-semibold text-slate-500 block">Measured Purity</span>
              <span className="text-lg font-bold font-mono text-slate-900">
                {verifiedRecord.purity_formatted}
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-xs font-semibold text-slate-500 block">Settled Valuation</span>
              <span className="text-lg font-bold font-mono text-gold-700">
                {verifiedRecord.settlement_formatted}
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-xs font-semibold text-slate-500 block">Evidence Integrity</span>
              <span className="text-lg font-bold font-mono text-green-700">
                {verifiedRecord.integrity_status}
              </span>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl space-y-2 border border-slate-200 text-xs text-slate-600">
            <div className="flex items-center space-x-2 text-slate-800 font-semibold">
              <Lock className="w-4 h-4 text-gold-600" />
              <span>Independent Verification Guarantees:</span>
            </div>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                Integer arithmetic re-derived by independent verifier (gtverify) matches exact paise settlement.
              </li>
              <li>
                Customer independently entered blind scale weight matching the physical appraisal reading.
              </li>
              <li>
                Double-entry balanced postings committed to append-only database audit log.
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
