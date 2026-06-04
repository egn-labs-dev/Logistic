import { Shield } from 'lucide-react';

export const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-10">
        <div className="flex items-center space-x-3 mb-8 border-b pb-6">
          <div className="bg-indigo-600 p-3 rounded-xl">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Privacy Policy</h1>
            <p className="text-slate-500">Effective Date: 2024-05-01</p>
          </div>
        </div>

        <div className="space-y-6 text-sm leading-relaxed text-slate-600">
          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">1. Introduction</h2>
            <p>Welcome to Zero Trust Dispatch LLC. We respect your privacy and are committed to protecting your personal data. This Privacy Policy explains how we collect, use, and safeguard your information when you use our enterprise logistics platform.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">2. Data We Collect</h2>
            <p>We may collect and process the following data:</p>
            <ul className="list-disc pl-5 mt-2 space-y-1">
              <li><strong>Account Information:</strong> Email addresses and passwords (securely hashed) of dispatchers.</li>
              <li><strong>Logistics Data:</strong> Cargo details, locations, and client messages processed through our platform.</li>
              <li><strong>Technical Data:</strong> IP addresses and browser information used for rate limiting, security monitoring, and fraud prevention.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">3. How We Use Artificial Intelligence (LLM)</h2>
            <p>Our core platform relies on Large Language Models (LLMs) to automate dispatching. We adhere to strict <strong>Zero Trust</strong> principles:</p>
            <ul className="list-disc pl-5 mt-2 space-y-1">
              <li><strong>Data Scrubber:</strong> Before any client message is sent to the LLM (e.g., Google Gemini), our proprietary Data Scrubber intercepts and anonymizes Personally Identifiable Information (PII) such as phone numbers, names, and exact addresses.</li>
              <li><strong>No AI Training:</strong> The anonymized data sent to third-party AI providers is explicitly not used to train their global models.</li>
              <li><strong>Live Deanonymization:</strong> PII remains encrypted and stored within our secure database vault. It is only dynamically re-attached (deanonymized) when a legally authorized dispatcher views the dashboard.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">4. Data Sharing and Security</h2>
            <p>We employ Row-Level Security (RLS) to ensure that your organization's data is strictly isolated. We do not sell your personal data to third parties. Data is only shared with trusted infrastructure providers (e.g., hosting, email services) strictly for operational purposes under GDPR-compliant Data Processing Agreements (DPAs).</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">5. Your GDPR Rights</h2>
            <p>If you are located in the European Economic Area (EEA), you have the right to access, correct, delete, or restrict the processing of your personal data. To exercise these rights, please contact our Data Protection Officer at privacy@zt-dispatch.com.</p>
          </section>
        </div>
      </div>
    </div>
  );
};
