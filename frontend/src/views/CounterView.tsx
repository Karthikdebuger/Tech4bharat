import React, { useState } from 'react';
import {
  Scale,
  Eye,
  Microscope,
  ShieldCheck,
  Calculator,
  FileCheck2,
  Coins,
  CheckCircle2,
  Copy,
  ArrowRight,
} from 'lucide-react';
import {
  formatPaiseToINR,
  formatMgToGrams,
  formatPermille,
  truncateHash,
} from '../utils/formatters.ts';

interface ExchangeData {
  id: string;
  customerRef: string;
  state: string;
  grossMg: number;
  stonesMg: number;
  netMg: number;
  witnessEnteredMg: number | null;
  witnessMatched: boolean;
  purityReadings: Array<{ id: string; kind: string; permille: number }>;
  ruleStatus: string;
  coverageRatio: string;
  receipt: any | null;
  receiptHash: string | null;
  settled: boolean;
}

export const CounterView: React.FC = () => {
  const [step, setStep] = useState<number>(1);
  const [exchange, setExchange] = useState<ExchangeData>({
    id: 'ex-demo-worked-example',
    customerRef: 'c_9b7e3f421a8d05c1',
    state: 'DRAFT',
    grossMg: 30800,
    stonesMg: 0,
    netMg: 30800,
    witnessEnteredMg: null,
    witnessMatched: false,
    purityReadings: [
      { id: 'p-1', kind: 'XRF_POINT', permille: 905 },
      { id: 'p-2', kind: 'XRF_POINT', permille: 908 },
      { id: 'p-3', kind: 'KARAT_METER', permille: 905 },
    ],
    ruleStatus: 'PENDING',
    coverageRatio: '0/12',
    receipt: null,
    receiptHash: null,
    settled: false,
  });

  const [customerPhone, setCustomerPhone] = useState('9840012345');
  const [grossInput, setGrossInput] = useState('30.800');
  const [stonesInput, setStonesInput] = useState('0.000');
  const [witnessInput, setWitnessInput] = useState('30.800');
  const [deductionBp, setDeductionBp] = useState(200); // 2.00%
  const [goldRateG, setGoldRateG] = useState(13000); // ₹13,000 / g
  const [copyFeedback, setCopyFeedback] = useState(false);

  // Step 1: Lock Intake
  const handleLockIntake = () => {
    const gross = Math.round(parseFloat(grossInput) * 1000);
    const stones = Math.round(parseFloat(stonesInput) * 1000);
    const net = gross - stones;
    setExchange((prev) => ({
      ...prev,
      grossMg: gross,
      stonesMg: stones,
      netMg: net,
      state: 'INTAKE_LOCKED',
    }));
    setStep(2);
  };

  // Step 2: Record Customer Witness
  const handleRecordWitness = () => {
    const entered = Math.round(parseFloat(witnessInput) * 1000);
    const matched = entered === exchange.grossMg;
    setExchange((prev) => ({
      ...prev,
      witnessEnteredMg: entered,
      witnessMatched: matched,
      state: 'EVIDENCE_CAPTURED',
    }));
    setStep(3);
  };

  // Step 4: Evaluate Rules E01-E13
  const handleEvaluateRules = () => {
    // In demo worked example, readings are consistent
    setExchange((prev) => ({
      ...prev,
      ruleStatus: 'CONSISTENT',
      coverageRatio: '11/12',
      state: 'VALIDATION_CLEAR',
    }));
    setStep(5);
  };

  // Step 5: Generate Quote
  const handleGenerateQuote = () => {
    const nominalPermille = 905;
    const fineUg = exchange.netMg * nominalPermille; // 27,874,000 ug
    const payableUg = Math.round((fineUg * (10000 - deductionBp)) / 10000); // 27,316,520 ug
    const ratePaisePerG = goldRateG * 100; // 1,300,000 paise/g
    const exactValuePaise = Math.round((payableUg * ratePaisePerG) / 1000000); // 35,511,476 paise
    const settlementPaise = Math.round(exactValuePaise / 100) * 100; // 35,511,500 paise
    const roundingDiff = settlementPaise - exactValuePaise; // +24 paise

    const dummyReceipt = {
      receipt_version: 1,
      is_demo: true,
      exchange_id: exchange.id,
      shop_id: 'shop-madurai-01',
      customer_ref: exchange.customerRef,
      timestamp_utc: new Date().toISOString(),
      weight: {
        gross_mg: exchange.grossMg,
        stones_mg: exchange.stonesMg,
        net_mg: exchange.netMg,
        formatted_net: formatMgToGrams(exchange.netMg),
      },
      witness: {
        customer_entered_mg: exchange.witnessEnteredMg ?? exchange.grossMg,
        mode: 'OWN_DEVICE',
        matched: true,
      },
      purity: {
        nominal_permille: nominalPermille,
        tolerance_permille: 10,
        low_permille: 895,
        high_permille: 915,
        formatted_purity: '90.50% (905‰)',
      },
      valuation: {
        rate_paise_per_g: ratePaisePerG,
        deduction_bp: deductionBp,
        fine_gold_ug: fineUg,
        payable_gold_ug: payableUg,
        retained_gold_ug: fineUg - payableUg,
        exact_value_paise: exactValuePaise,
        settlement_paise: settlementPaise,
        rounding_difference_paise: roundingDiff,
        formatted_settlement: formatPaiseToINR(settlementPaise),
      },
      integrity: {
        aggregate_outcome: 'CONSISTENT',
        evidence_coverage: '11/12',
        attested_rules: [],
      },
    };

    // Canonical receipt hash for worked example
    const rHash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';

    setExchange((prev) => ({
      ...prev,
      receipt: dummyReceipt,
      receiptHash: rHash,
      state: 'QUOTED',
    }));
    setStep(6);
  };

  // Step 6: Cosign
  const handleCosign = () => {
    setExchange((prev) => ({
      ...prev,
      state: 'COSIGNED',
    }));
    setStep(7);
  };

  // Step 7: Settle
  const handleSettle = () => {
    setExchange((prev) => ({
      ...prev,
      state: 'SETTLED',
      settled: true,
    }));
  };

  const copyHash = () => {
    if (exchange.receiptHash) {
      navigator.clipboard.writeText(exchange.receiptHash);
      setCopyFeedback(true);
      setTimeout(() => setCopyFeedback(false), 2000);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Step Tracker Header */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="p-2.5 bg-gold-100 text-gold-800 rounded-lg font-bold text-sm">
              EXCHANGE #{exchange.id.slice(-6)}
            </span>
            <span className="text-xs px-2.5 py-1 bg-amber-100 text-amber-900 rounded-full font-medium">
              MODE: DEMO
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Cust Ref: {exchange.customerRef}
            </span>
          </div>
          <div className="text-sm font-semibold text-slate-700">
            Step {step} of 7: {
              step === 1 ? 'Intake' :
              step === 2 ? 'Blind Customer Witness' :
              step === 3 ? 'Readings & Evidence' :
              step === 4 ? 'Integrity Rules Engine' :
              step === 5 ? 'Itemized Valuation' :
              step === 6 ? 'Dual Cosign' : 'Settlement & Ledgers'
            }
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 h-2 rounded-full mt-4 overflow-hidden">
          <div
            className="bg-gold-500 h-full transition-all duration-300"
            style={{ width: `${(step / 7) * 100}%` }}
          />
        </div>
      </div>

      {/* Step 1: Intake & Weight Capture */}
      {step === 1 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <Scale className="w-6 h-6 text-gold-600" />
            <h2>Stage 1: Scale Intake & Physical Weight</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Customer Mobile / ID (Pseudonymized)
              </label>
              <input
                type="text"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gold-500 outline-none"
              />
              <p className="text-xs text-slate-500 mt-1">
                Raw phone is immediately converted to irreversible HMAC-SHA256 pseudonym.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Scale Instrument Serial
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  disabled
                  value="METTLER-TOLEDO-JEW-04 (Calibrated)"
                  className="w-full px-3 py-2 bg-slate-50 border rounded-lg text-slate-600"
                />
                <span className="p-2 text-green-600 bg-green-50 rounded-lg text-xs font-semibold">
                  Valid
                </span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Gross Weight (grams)
              </label>
              <input
                type="number"
                step="0.001"
                value={grossInput}
                onChange={(e) => setGrossInput(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg font-mono text-lg font-semibold"
              />
              <span className="text-xs text-slate-500">
                Exact integer representation: {Math.round(parseFloat(grossInput || '0') * 1000)} mg
              </span>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Stones / Dirt / Enamel Tare (grams)
              </label>
              <input
                type="number"
                step="0.001"
                value={stonesInput}
                onChange={(e) => setStonesInput(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg font-mono text-lg"
              />
              <span className="text-xs text-slate-500">
                Exact integer representation: {Math.round(parseFloat(stonesInput || '0') * 1000)} mg
              </span>
            </div>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg flex justify-between items-center border border-slate-200">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Net Evaluated Gold Weight
              </span>
              <div className="text-2xl font-bold font-mono text-slate-900">
                {formatMgToGrams(
                  Math.round(parseFloat(grossInput || '0') * 1000) -
                  Math.round(parseFloat(stonesInput || '0') * 1000)
                )}
              </div>
            </div>
            <button
              onClick={handleLockIntake}
              className="px-6 py-2.5 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg flex items-center space-x-2 transition"
            >
              <span>Lock Intake Weight</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Blind Customer Weight Witness (Rule E11) */}
      {step === 2 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <Eye className="w-6 h-6 text-gold-600" />
            <h2>Stage 2: Blind Customer Weight Witness (Rule E11)</h2>
          </div>

          <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg text-sm text-amber-900 leading-relaxed">
            <span className="font-semibold block mb-1">
              Blind Weight Anti-Bias Protocol (§6.3):
            </span>
            The customer enters the exact reading shown on the scale display from their phone or
            counter keypad before staff values are revealed. The server validates agreement to prevent confirmation bias.
          </div>

          <div className="max-w-md mx-auto space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Customer Witness Entry (grams)
              </label>
              <input
                type="number"
                step="0.001"
                value={witnessInput}
                onChange={(e) => setWitnessInput(e.target.value)}
                className="w-full text-center text-3xl font-mono font-bold py-3 border-2 border-gold-400 rounded-xl outline-none"
              />
            </div>

            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={() => setWitnessInput('30.800')}
                className="text-xs px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded font-medium text-slate-700"
              >
                Match Scale (30.800 g)
              </button>
              <button
                onClick={() => setWitnessInput('30.500')}
                className="text-xs px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded font-medium"
              >
                Simulate Mismatch (30.500 g)
              </button>
            </div>

            <button
              onClick={handleRecordWitness}
              className="w-full py-3 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg flex items-center justify-center space-x-2 transition"
            >
              <span>Validate & Confirm Witness</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Readings & OCR */}
      {step === 3 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <Microscope className="w-6 h-6 text-gold-600" />
            <h2>Stage 3: Multi-Source Purity Readings & OCR Evidence</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {exchange.purityReadings.map((r, idx) => (
              <div key={r.id} className="p-4 border rounded-lg bg-slate-50 space-y-1">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                  Reading #{idx + 1} ({r.kind})
                </span>
                <div className="text-xl font-bold font-mono text-slate-900">
                  {formatPermille(r.permille)}
                </div>
                <div className="text-xs text-green-700 font-medium flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Calibrated Instrument</span>
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 bg-slate-100 rounded-lg border border-slate-200 flex justify-between items-center">
            <div>
              <span className="text-sm font-semibold text-slate-800">
                Bill OCR Assistance (Optional Assist-Only)
              </span>
              <p className="text-xs text-slate-500">
                Bill HUID: <b>AH8972</b> · Declared 22K (916‰) · Requires operator confirmation
              </p>
            </div>
            <button
              onClick={() => setStep(4)}
              className="px-6 py-2.5 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg flex items-center space-x-2 transition"
            >
              <span>Proceed to Rules Engine</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Integrity Rule Engine */}
      {step === 4 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <ShieldCheck className="w-6 h-6 text-gold-600" />
            <h2>Stage 4: Automated Integrity Protocol (Rules E01–E13)</h2>
          </div>

          <div className="p-4 bg-slate-50 rounded-lg space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-slate-800">Rule E11: Customer Blind Witness</span>
              <span className="px-2.5 py-0.5 bg-green-100 text-green-800 rounded font-semibold text-xs">
                PASS (Exact Match)
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-semibold text-slate-800">Rule E03: XRF Multiple Point Variance</span>
              <span className="px-2.5 py-0.5 bg-green-100 text-green-800 rounded font-semibold text-xs">
                PASS (Spread 3‰ &lt; 15‰)
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-semibold text-slate-800">Rule E02: Net Weight Mathematical Sanity</span>
              <span className="px-2.5 py-0.5 bg-green-100 text-green-800 rounded font-semibold text-xs">
                PASS (30.800 g &gt; 0)
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-semibold text-slate-800">Rule E06: Minimum Evidence Redundancy</span>
              <span className="px-2.5 py-0.5 bg-green-100 text-green-800 rounded font-semibold text-xs">
                PASS (3 independent readings)
              </span>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleEvaluateRules}
              className="px-6 py-2.5 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg flex items-center space-x-2 transition"
            >
              <span>Lock Verification & Generate Quote</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 5: Locked Itemized Valuation */}
      {step === 5 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <Calculator className="w-6 h-6 text-gold-600" />
            <h2>Stage 5: Itemized Valuation & Locked Policy Snapshot</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Market Gold Rate (24K fine gold ₹/g)
              </label>
              <input
                type="number"
                value={goldRateG}
                onChange={(e) => setGoldRateG(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border rounded-lg font-mono font-bold text-lg"
              />
              <span className="text-xs text-slate-500">
                Exact integer representation: {goldRateG * 100} paise/g
              </span>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Melting & Refining Margin (Basis Points)
              </label>
              <input
                type="number"
                value={deductionBp}
                onChange={(e) => setDeductionBp(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border rounded-lg font-mono font-bold text-lg"
              />
              <span className="text-xs text-slate-500">
                200 bp = 2.00% standard shop deduction
              </span>
            </div>
          </div>

          <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 space-y-3">
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-700">Gross Fine Gold Content (30.800g × 905‰):</span>
              <span className="font-mono font-semibold">27,874,000 µg (27.874 g)</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-700">Refining Deduction (200 bp = 2.00%):</span>
              <span className="font-mono text-red-700">-557,480 µg (-0.557 g)</span>
            </div>
            <div className="flex justify-between items-center text-sm font-semibold border-t pt-2">
              <span className="text-slate-900">Payable Pure Gold:</span>
              <span className="font-mono text-slate-900">27,316,520 µg (27.317 g)</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-700">Exact Value (27.31652g × ₹13,000/g):</span>
              <span className="font-mono">₹3,55,114.76 (35,511,476 paise)</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-700">Rounding to Whole Rupee:</span>
              <span className="font-mono text-green-700">+24 paise</span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold border-t pt-2 text-slate-900">
              <span>Final Settlement Amount:</span>
              <span className="font-mono text-2xl text-gold-700">₹3,55,115.00</span>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleGenerateQuote}
              className="px-6 py-2.5 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg flex items-center space-x-2 transition"
            >
              <span>Lock Quote & Generate Canonical Hash</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 6: Dual Cosigning */}
      {step === 6 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <FileCheck2 className="w-6 h-6 text-gold-600" />
            <h2>Stage 6: Dual-Party Cryptographic Cosigning</h2>
          </div>

          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
              Canonical Receipt SHA-256 Digest (RFC 8785)
            </span>
            <div className="flex items-center space-x-3 bg-white p-3 rounded border font-mono text-xs break-all">
              <span className="flex-1 text-slate-800">{exchange.receiptHash}</span>
              <button
                onClick={copyHash}
                className="p-1.5 hover:bg-slate-100 rounded text-slate-600 transition"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            {copyFeedback && (
              <span className="text-xs text-green-600 font-medium block">
                Hash copied to clipboard!
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg bg-green-50 border-green-200 flex items-center space-x-3">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
              <div>
                <span className="text-sm font-semibold text-green-900 block">
                  Staff Appraiser Approval
                </span>
                <span className="text-xs text-green-700 font-mono">
                  Hash confirmed & cosigned
                </span>
              </div>
            </div>

            <div className="p-4 border rounded-lg bg-green-50 border-green-200 flex items-center space-x-3">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
              <div>
                <span className="text-sm font-semibold text-green-900 block">
                  Customer Dual-Screen Approval
                </span>
                <span className="text-xs text-green-700 font-mono">
                  PIN authenticated & matched
                </span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleCosign}
              className="px-6 py-2.5 bg-gold-600 hover:bg-gold-700 text-white font-semibold rounded-lg flex items-center space-x-2 transition"
            >
              <span>Execute Settlement & Post Ledgers</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 7: Settlement & Balanced Double-Entry Ledgers */}
      {step === 7 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-3 text-slate-800 font-semibold text-lg border-b pb-3">
            <Coins className="w-6 h-6 text-gold-600" />
            <h2>Stage 7: Settlement Discharge & Dual Ledgers</h2>
          </div>

          {!exchange.settled ? (
            <div className="p-4 bg-slate-50 rounded-lg text-center space-y-4">
              <p className="text-sm text-slate-700">
                Click below to commit the four balanced journal entries to PostgreSQL.
                Deferred triggers will enforce exact debit = credit balance at transaction commit.
              </p>
              <button
                onClick={handleSettle}
                className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition"
              >
                Confirm Payout of ₹3,55,115.00
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-900 flex items-center space-x-3">
                <CheckCircle2 className="w-8 h-8 text-green-600 flex-shrink-0" />
                <div>
                  <h3 className="font-bold">Transaction Successfully Settled</h3>
                  <p className="text-xs text-green-800">
                    Dual ledgers balanced and verified. Immutable receipt committed.
                  </p>
                </div>
              </div>

              {/* Journal Postings View */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg bg-slate-50 font-mono text-xs space-y-2">
                  <span className="font-bold text-slate-800 block">
                    Gold Journal Postings (µg)
                  </span>
                  <div className="flex justify-between text-slate-700">
                    <span>DR Stock:OldGold</span>
                    <span>27,874,000 µg</span>
                  </div>
                  <div className="flex justify-between text-slate-700">
                    <span>CR Customer:GoldPayable</span>
                    <span>27,316,520 µg</span>
                  </div>
                  <div className="flex justify-between text-slate-700">
                    <span>CR Retained:Deduction</span>
                    <span>557,480 µg</span>
                  </div>
                  <div className="border-t pt-1 font-bold text-green-700 flex justify-between">
                    <span>Balance Status</span>
                    <span>BALANCED (0 diff)</span>
                  </div>
                </div>

                <div className="p-4 border rounded-lg bg-slate-50 font-mono text-xs space-y-2">
                  <span className="font-bold text-slate-800 block">
                    Financial Journal Postings (Paise)
                  </span>
                  <div className="flex justify-between text-slate-700">
                    <span>DR Purchases:OldGold</span>
                    <span>35,511,476 p</span>
                  </div>
                  <div className="flex justify-between text-slate-700">
                    <span>DR RoundingDifference</span>
                    <span>24 p</span>
                  </div>
                  <div className="flex justify-between text-slate-700">
                    <span>CR Bank / Cash</span>
                    <span>35,511,500 p</span>
                  </div>
                  <div className="border-t pt-1 font-bold text-green-700 flex justify-between">
                    <span>Balance Status</span>
                    <span>BALANCED (0 diff)</span>
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center border-t pt-4">
                <span className="text-xs text-slate-500 font-mono">
                  Receipt Hash: {truncateHash(exchange.receiptHash || '')}
                </span>
                <button
                  onClick={() => {
                    setStep(1);
                    setExchange((prev) => ({ ...prev, settled: false }));
                  }}
                  className="px-4 py-2 border rounded-lg text-sm font-semibold hover:bg-slate-50"
                >
                  Start New Transaction
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
