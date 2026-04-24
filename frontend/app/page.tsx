import Link from 'next/link';
import { CheckCircle2, Zap, Shield, Sparkles, ArrowRight } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative">
        {/* Hero Section */}
        <div className="flex flex-col items-center justify-center min-h-screen px-4 text-center">
          <div className="animate-fadeIn">
            {/* Logo */}
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-2xl shadow-blue-500/30 mb-8 animate-pulse-glow">
              <CheckCircle2 className="w-10 h-10 text-white" />
            </div>

            {/* Heading */}
            <h1 className="text-6xl md:text-7xl font-bold mb-6 animate-slideIn">
              <span className="text-gradient">TaskFlow</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-2xl animate-slideIn" style={{ animationDelay: '0.1s' }}>
              Modern task management for productive teams. Simple, powerful, and beautiful.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-slideIn" style={{ animationDelay: '0.2s' }}>
              <Link
                href="/register"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all duration-300 hover:-translate-y-1 inline-flex items-center justify-center gap-2"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/login"
                className="px-8 py-4 bg-white/10 text-white rounded-xl font-semibold backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-1"
              >
                Sign In
              </Link>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto animate-fadeIn" style={{ animationDelay: '0.3s' }}>
              <div className="glass p-6 rounded-xl hover:bg-white/10 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Zap className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Lightning Fast</h3>
                <p className="text-gray-400 text-sm">Blazing fast performance with real-time updates</p>
              </div>

              <div className="glass p-6 rounded-xl hover:bg-white/10 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Shield className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Secure & Private</h3>
                <p className="text-gray-400 text-sm">Enterprise-grade security for your data</p>
              </div>

              <div className="glass p-6 rounded-xl hover:bg-white/10 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-lg bg-pink-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-6 h-6 text-pink-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Beautiful UI</h3>
                <p className="text-gray-400 text-sm">Clean, modern interface you'll love to use</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
