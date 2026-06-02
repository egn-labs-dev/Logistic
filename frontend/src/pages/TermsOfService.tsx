import { FileText } from 'lucide-react';

export const TermsOfService = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-10">
        <div className="flex items-center space-x-3 mb-8 border-b pb-6">
          <div className="bg-indigo-600 p-3 rounded-xl">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Terms of Service</h1>
            <p className="text-slate-500">Effective Date: {new Date().toLocaleDateString()}</p>
          </div>
        </div>

        <div className="space-y-6 text-sm leading-relaxed text-slate-600">
          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">1. Acceptance of Terms</h2>
            <p>By accessing or using the Zero Trust Dispatch LLC ("Company") logistics platform, you agree to be bound by these Terms of Service. If you do not agree to all the terms and conditions, you may not access the service.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">2. Service Description</h2>
            <p>Zero Trust Dispatch provides an enterprise-grade Software-as-a-Service (SaaS) platform that leverages Artificial Intelligence for automated cargo dispatching, utilizing a Human-in-the-Loop (HITL) approach for secure session interception and management.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">3. User Responsibilities and Security</h2>
            <ul className="list-disc pl-5 mt-2 space-y-1">
              <li>You are responsible for maintaining the confidentiality of your account credentials (email and password).</li>
              <li>You must immediately notify us of any unauthorized use of your account.</li>
              <li>The Service utilizes Zero Trust architecture (Row-Level Security). You agree not to attempt to bypass, exploit, or probe the security mechanisms of the platform.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">4. AI and Automation Acknowledgment</h2>
            <p>You acknowledge that the Service utilizes Large Language Models (LLMs) to process logistics requests automatically. While we employ strict safety measures and Data Scrubbing to protect Personal Identifiable Information (PII), the Company is not liable for errors in AI interpretation. The platform is designed with a "Human-in-the-Loop" fallback, and it is the responsibility of your dispatchers to intervene when alerts are triggered.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">5. Limitation of Liability</h2>
            <p>In no event shall Zero Trust Dispatch LLC be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the Service.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">6. Governing Law</h2>
            <p>These Terms shall be governed and construed in accordance with the laws of the applicable jurisdiction, without regard to its conflict of law provisions.</p>
          </section>
        </div>
      </div>
    </div>
  );
};
