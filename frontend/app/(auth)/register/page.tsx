import RegisterForm from '@/components/auth/RegisterForm';
import Link from 'next/link';
import { CheckCircle2, ArrowRight } from 'lucide-react';

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-md w-full">
        {/* Logo/Brand */}
        <div className="text-center mb-8 animate-fadeIn">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-2xl shadow-blue-500/30 mb-4">
            <CheckCircle2 className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gradient mb-2">Get Started</h1>
          <p className="text-gray-400">Create your account to start organizing</p>
        </div>

        {/* Register Card */}
        <div className="glass-strong rounded-2xl shadow-2xl p-8 animate-scaleIn">
          <RegisterForm />

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400">
              Already have an account?{' '}
              <Link
                href="/login"
                className="text-blue-400 hover:text-blue-300 font-medium inline-flex items-center gap-1 transition-colors group"
              >
                Sign in
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-8 animate-fadeIn">
          By signing up, you agree to our Terms & Privacy Policy
        </p>
      </div>
    </div>
  );
}