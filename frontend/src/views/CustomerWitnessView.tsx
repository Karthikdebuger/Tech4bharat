import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, Globe2 } from 'lucide-react';

export const CustomerWitnessView: React.FC = () => {
  const [lang, setLang] = useState<'en' | 'ta'>('en');
  const [digits, setDigits] = useState<string>('');
  const [submitted, setSubmitted] = useState<boolean>(false);

  const handleDigit = (d: string) => {
    if (d === 'C') {
      setDigits('');
    } else if (d === '.') {
      if (!digits.includes('.')) {
        setDigits((prev) => prev + '.');
      }
    } else {
      if (digits.length < 8) {
        setDigits((prev) => prev + d);
      }
    }
  };

  const handleSubmit = () => {
    if (digits.length > 0) {
      setSubmitted(true);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 space-y-6">
      {/* Language Header */}
      <div className="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200">
        <div className="flex items-center space-x-2 text-slate-800 font-semibold text-sm">
          <ShieldCheck className="w-5 h-5 text-gold-600" />
          <span>Gold Trust Customer Witness</span>
        </div>
        <button
          onClick={() => setLang(lang === 'en' ? 'ta' : 'en')}
          className="flex items-center space-x-1 px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-xs font-semibold text-slate-700"
        >
          <Globe2 className="w-3.5 h-3.5" />
          <span>{lang === 'en' ? 'தமிழ்' : 'English'}</span>
        </button>
      </div>

      {!submitted ? (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-xl font-bold text-slate-900">
              {lang === 'en'
                ? 'Read the Scale Display'
                : 'எடையளவு திரையைப் பார்த்து தட்டச்சு செய்யவும்'}
            </h2>
            <p className="text-xs text-slate-600 leading-relaxed">
              {lang === 'en'
                ? 'Please type the numbers shown directly on the weighing scale. Your entry is recorded independently before staff calculations.'
                : 'எடை இயந்திரத் திரையில் தெரியும் எண்களை உள்ளிடவும். உங்கள் பதிவு பணியாளர்களின் மதிப்பீட்டுக்கு முன்பே சுயாதீனமாக பதியப்படுகிறது.'}
            </p>
          </div>

          {/* Number Display */}
          <div className="bg-slate-50 border-2 border-gold-400 rounded-xl py-4 text-center">
            <span className="font-mono text-4xl font-extrabold text-slate-900 tracking-wider">
              {digits || '0.000'}
            </span>
            <span className="text-sm font-semibold text-slate-500 ml-2">g</span>
          </div>

          {/* Keypad */}
          <div className="grid grid-cols-3 gap-3">
            {['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'C'].map((k) => (
              <button
                key={k}
                onClick={() => handleDigit(k)}
                className="py-4 bg-slate-100 hover:bg-slate-200 active:bg-slate-300 rounded-xl font-mono text-xl font-bold text-slate-800 transition"
              >
                {k}
              </button>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={!digits}
            className="w-full py-3.5 bg-gold-600 hover:bg-gold-700 disabled:opacity-50 text-white font-bold rounded-xl shadow-md transition"
          >
            {lang === 'en' ? 'Confirm Weight' : 'எடையை உறுதிசெய்'}
          </button>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6 text-center">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-10 h-10" />
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-900">
              {lang === 'en' ? 'Witness Recorded!' : 'எடை பதிவு செய்யப்பட்டது!'}
            </h3>
            <p className="text-xs text-slate-600">
              {lang === 'en'
                ? `You witnessed ${digits} g. Once appraisal is complete, the itemized quote will appear here for your approval.`
                : `நீங்கள் ${digits} கிராம் என உறுதி செய்துள்ளீர்கள். மதிப்பீடு முடிந்ததும் விவரமான கணக்கீடு உங்கள் பார்வைக்கு வரும்.`}
            </p>
          </div>

          {/* Transparent calculation explainer item */}
          <div className="bg-slate-50 p-4 rounded-xl text-left border border-slate-200 space-y-2 text-xs">
            <span className="font-semibold text-slate-800 block">
              {lang === 'en' ? 'Guaranteed Trust Promise:' : 'நம்பகத்தன்மை உத்தரவாதம்:'}
            </span>
            <p className="text-slate-600">
              {lang === 'en'
                ? 'No money or pure gold weight can be deducted without being itemized and cryptographically signed on your digital receipt.'
                : 'உங்கள் டிஜிட்டல் ரசீதில் வெளிப்படையாகக் காட்டப்படாமல் எந்தக் கழிவும் அல்லது பணப் பிடித்தமும் செய்யப்படாது.'}
            </p>
          </div>

          <button
            onClick={() => {
              setSubmitted(false);
              setDigits('');
            }}
            className="text-xs text-slate-500 hover:text-slate-800 underline"
          >
            {lang === 'en' ? 'Re-enter reading' : 'மீண்டும் உள்ளிடவும்'}
          </button>
        </div>
      )}
    </div>
  );
};
