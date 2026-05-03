# Frontend Code Audit Report
**Date:** 2026-04-19  
**Auditor:** Professional Web Developer Review

## Executive Summary
The frontend codebase is well-structured with Next.js 14+ App Router, TypeScript, and proper component separation. However, there are **critical issues** that will prevent the application from working correctly.

---

## 🔴 Critical Issues (Must Fix)

### 1. **Missing Username Field in Registration**
**Location:** `context/AuthContext.tsx:38-45`

**Problem:**
- Backend expects `{ email, password }` ✅
- Frontend sends `{ email, password }` ✅
- **BUT** the backend schema `UserRegister` only has `email` and `password` fields
- No username field is required or sent

**Status:** ✅ Actually correct - no issue here

### 2. **Dependency Mismatch - React 19 with Next.js 16**
**Location:** `package.json:14-19`

**Problem:**
```json
"next": "^16.0.0",      // Next.js 16 doesn't exist yet (latest is 14.x)
"react": "^19.0.0",     // React 19 is experimental/canary
"react-dom": "^19.0.0"
```

**Impact:**
- Unstable/experimental versions
- Potential runtime errors
- Missing features or breaking changes

**Fix:**
```json
"next": "^14.2.0",
"react": "^18.3.0",
"react-dom": "^18.3.0"
```

### 3. **Unused Dependency - better-auth**
**Location:** `package.json:18`

**Problem:**
- `better-auth` is installed but never imported or used
- Custom JWT auth is implemented instead
- Adds unnecessary bundle size

**Fix:** Remove from dependencies

### 4. **Missing Loading State in AuthContext**
**Location:** `context/AuthContext.tsx:9-16`

**Problem:**
```tsx
const [user, setUser] = useState<User | null>(null);
const [isAuthenticated, setIsAuthenticated] = useState(false);
// ❌ No loading state
```

**Impact:**
- On app load, `checkAuth()` runs but UI doesn't know it's loading
- Components render before auth state is determined
- Flash of wrong content (login page → tasks page)

**Fix:**
```tsx
const [loading, setLoading] = useState(true);

const checkAuth = async () => {
  try {
    const userData = await apiClient.get<User>('/api/v1/auth/me');
    setUser(userData);
    setIsAuthenticated(true);
  } catch (error) {
    setUser(null);
    setIsAuthenticated(false);
  } finally {
    setLoading(false);
  }
};
```

### 5. **Missing Error Handling in API Client**
**Location:** `lib/api-client.ts:29-36`

**Problem:**
```tsx
if (!response.ok) {
  const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
  throw new Error(error.detail || `HTTP error! status: ${response.status}`);
}
```

**Issues:**
- No handling for 401 (unauthorized) to trigger logout
- No handling for network errors
- No retry logic for failed requests

### 6. **CSRF Token Not Sent with Requests**
**Location:** `lib/api-client.ts:20-27`

**Problem:**
- Backend sets CSRF token in response header: `X-CSRF-Token`
- Backend expects CSRF token in request header for state-changing operations
- Frontend never stores or sends CSRF token

**Impact:**
- POST/PUT/DELETE requests may fail with 403 Forbidden
- CSRF protection is bypassed

**Fix:** Store CSRF token from login response and include in subsequent requests

---

## ⚠️ Major Issues (Should Fix)

### 7. **No Error Boundary**
**Location:** `app/layout.tsx`

**Problem:**
- No React Error Boundary to catch runtime errors
- App crashes completely on unhandled errors

**Fix:** Add error boundary component

### 8. **Missing Input Validation Component**
**Location:** `components/ui/Input.tsx` (file exists but not reviewed)

**Concern:** Need to verify proper validation and accessibility

### 9. **Hardcoded API URL in Production**
**Location:** `lib/api-client.ts:1`

```tsx
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Problem:**
- Fallback to localhost in production if env var missing
- Should fail loudly instead

### 10. **No Request Cancellation**
**Location:** `hooks/useTasks.ts`, `context/AuthContext.tsx`

**Problem:**
- API requests not cancelled when component unmounts
- Can cause memory leaks and state updates on unmounted components

**Fix:** Use AbortController

---

## 🟡 Minor Issues (Nice to Have)

### 11. **Missing TypeScript Strict Mode**
**Location:** `tsconfig.json` (not reviewed)

**Recommendation:** Enable strict mode for better type safety

### 12. **No Loading Skeleton**
**Location:** `app/(dashboard)/tasks/page.tsx:73-74`

```tsx
{loading && tasks.length === 0 ? (
  <div className="text-center py-12 text-gray-500">Loading tasks...</div>
) : (
```

**Improvement:** Use skeleton loaders instead of text

### 13. **Inline Confirm Dialog**
**Location:** `components/tasks/TaskItem.tsx:27`

```tsx
if (confirm('Are you sure you want to delete this task?')) {
```

**Issue:** Native confirm() is not customizable and looks unprofessional

**Fix:** Create custom confirmation modal

### 14. **No Optimistic Updates**
**Location:** `hooks/useTasks.ts`

**Improvement:** Update UI immediately, rollback on error

### 15. **Missing Accessibility Labels**
**Location:** Multiple components

**Issues:**
- Checkbox in TaskItem has no aria-label
- Modal has no aria-describedby
- Form errors not announced to screen readers

### 16. **No Request Debouncing**
**Location:** `components/tasks/TaskForm.tsx`

**Improvement:** Debounce form submission to prevent double-clicks

### 17. **Environment Variables Not Validated**
**Location:** `.env.local`

**Problem:**
- No validation that required env vars are present
- App may fail silently

---

## ✅ Good Practices Found

1. **Proper separation of concerns** - hooks, components, context, lib
2. **TypeScript usage** - proper typing throughout
3. **Client/Server component distinction** - proper 'use client' directives
4. **Tailwind CSS** - consistent styling approach
5. **Form validation** - password strength validation in RegisterForm
6. **HTTP-only cookies** - secure token storage
7. **Credentials included** - proper cookie handling in API client
8. **Loading states** - most components handle loading properly
9. **Error messages** - user-friendly error display

---

## Priority Fix Order

1. **Fix React/Next.js versions** (Critical - may not run)
2. **Add loading state to AuthContext** (Critical - UX issue)
3. **Implement CSRF token handling** (Critical - security/functionality)
4. **Add 401 handling in API client** (Critical - auth flow broken)
5. **Remove unused better-auth** (Major - bundle size)
6. **Add Error Boundary** (Major - stability)
7. **Add request cancellation** (Major - memory leaks)
8. **Improve accessibility** (Minor - compliance)
9. **Add optimistic updates** (Minor - UX enhancement)

---

## Estimated Fix Time
- Critical issues: 2-3 hours
- Major issues: 2-4 hours
- Minor issues: 4-6 hours
- **Total: 8-13 hours**
