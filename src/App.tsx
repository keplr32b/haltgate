import { type ReactNode, useMemo, useState } from 'react';
import {
  Activity,
  AlertOctagon,
  ArrowRight,
  BadgeCheck,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleDot,
  Code2,
  Copy,
  ExternalLink,
  FileCode2,
  Filter,
  Globe2,
  Hash,
  Info,
  KeyRound,
  LayoutDashboard,
  Link2,
  LockKeyhole,
  Plus,
  Radio,
  RefreshCw,
  Search,
  Send,
  Server,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Siren,
  Terminal,
  XCircle,
} from 'lucide-react';
import {
  Link,
  Route,
  Switch,
  useLocation,
  Router as WouterRouter,
} from 'wouter';

type Status = 'REGISTERED' | 'EVIDENCE' | 'ADJUDICATED';

type Verdict =
  | 'CONFIRMED'
  | 'CLEAR'
  | 'INCONCLUSIVE'
  | null;

type TargetCase = {
  targetId: string;
  label: string;
  status: Status;
  verdict: Verdict;
  halted: boolean;
  evidenceUrl: string;
  evidenceHost: string;
  submittedAt: string;
  adjudicatedAt: string;
  note: string;
  criteria: string;
  confidence: number;
  reporter: string;
};

type ActivityEvent = {
  type:
    | 'evidence'
    | 'adjudication'
    | 'halt'
    | 'clear'
    | 'registration';
  targetId: string;
  timestamp: string;
  description: string;
  actor: string;
};

type ContractMeta = {
  address: string;
  network: string;
  deploymentTx: string;
  owner: string;
  allowedHosts: string[];
  methods: {
    name: string;
    signature: string;
    description: string;
    kind: 'read' | 'write';
  }[];
};

const seedCases: TargetCase[] = [
  {
    targetId: 'TGT-0142',
    label: 'Bridge relayer / withdrawal proof',
    status: 'EVIDENCE',
    verdict: null,
    halted: true,
    evidenceUrl:
      'https://security.genlayer.com/advisories/GL-2025-014',
    evidenceHost: 'security.genlayer.com',
    submittedAt: '2025-02-18T09:42:00Z',
    adjudicatedAt: '',
    note:
      'Withdrawal proof accepts a stale quorum snapshot under a specific relay ordering.',
    criteria:
      'Public exploit evidence with reproducible impact against canonical relayer deployment.',
    confidence: 86,
    reporter: '0x4b9…c120',
  },
  {
    targetId: 'TGT-0138',
    label: 'Validator gateway / signature domain',
    status: 'ADJUDICATED',
    verdict: 'CONFIRMED',
    halted: true,
    evidenceUrl:
      'https://audit.genlayer.com/reports/validator-gateway',
    evidenceHost: 'audit.genlayer.com',
    submittedAt: '2025-02-16T14:08:00Z',
    adjudicatedAt: '2025-02-17T11:36:00Z',
    note:
      'Domain separator omission permits cross-context signature replay on gateway v2.',
    criteria:
      'Two independent public sources or one directly reproducible exploit report.',
    confidence: 94,
    reporter: '0x91a…af08',
  },
  {
    targetId: 'TGT-0129',
    label: 'Indexer API / historical pagination',
    status: 'ADJUDICATED',
    verdict: 'CLEAR',
    halted: false,
    evidenceUrl:
      'https://status.genlayer.com/incidents/2025-011',
    evidenceHost: 'status.genlayer.com',
    submittedAt: '2025-02-12T08:21:00Z',
    adjudicatedAt: '2025-02-13T16:02:00Z',
    note:
      'Reported pagination gap was isolated to a read replica and did not affect finality.',
    criteria:
      'Evidence must demonstrate impact to protocol safety or operator control plane.',
    confidence: 91,
    reporter: '0x3de…7c1e',
  },
  {
    targetId: 'TGT-0117',
    label: 'Consensus executor / callback timeout',
    status: 'REGISTERED',
    verdict: null,
    halted: false,
    evidenceUrl: '',
    evidenceHost: '',
    submittedAt: '2025-02-08T18:14:00Z',
    adjudicatedAt: '',
    note:
      'Target registered for monitoring. Awaiting public evidence before any halt action.',
    criteria:
      'Observable callback failure with a credible path to unsafe state transition.',
    confidence: 0,
    reporter: '0x0c8…1f42',
  },
  {
    targetId: 'TGT-0104',
    label: 'RPC quorum / stale block propagation',
    status: 'ADJUDICATED',
    verdict: 'INCONCLUSIVE',
    halted: false,
    evidenceUrl:
      'https://research.genlayer.org/rpc-quorum-notes',
    evidenceHost: 'research.genlayer.org',
    submittedAt: '2025-02-01T12:44:00Z',
    adjudicatedAt: '2025-02-03T10:19:00Z',
    note:
      'Observed divergence could not be attributed to the canonical RPC quorum.',
    criteria:
      'Evidence must identify target and show a repeatable protocol-level consequence.',
    confidence: 58,
    reporter: '0xa72…d905',
  },
];

const seedActivity: ActivityEvent[] = [
  {
    type: 'evidence',
    targetId: 'TGT-0142',
    timestamp: '18 min ago',
    description: 'Public evidence accepted for review',
    actor: '0x4b9…c120',
  },
  {
    type: 'adjudication',
    targetId: 'TGT-0129',
    timestamp: '2h ago',
    description: 'Consensus outcome recorded: CLEAR',
    actor: 'HaltGate consensus',
  },
  {
    type: 'halt',
    targetId: 'TGT-0138',
    timestamp: 'yesterday',
    description:
      'Target halt remains active after CONFIRMED verdict',
    actor: 'Owner 0x91a…af08',
  },
  {
    type: 'registration',
    targetId: 'TGT-0117',
    timestamp: '2d ago',
    description:
      'New target registered in canonical registry',
    actor: 'Owner 0x0c8…1f42',
  },
];

const contract: ContractMeta = {
  address: '0x67b8AAB3caD42b55eF2Fe7fE72fF33CF8413E27A',
  network: 'GenLayer Studionet',
  deploymentTx: '0x2f849613…0d6201',
  owner: 'Owner-controlled · read from contract',
  allowedHosts: [
    'security.genlayer.com',
    'audit.genlayer.com',
    'status.genlayer.com',
    'research.genlayer.org',
  ],
  methods: [
    {
      name: 'allow_host',
      signature: 'allow_host(host: str)',
      description: 'Owner allowlists a public evidence host.',
      kind: 'write',
    },
    {
      name: 'register_target',
      signature:
        'register_target(target_id: str, criteria_text: str)',
      description:
        'Owner creates a registered target case with sealed criteria.',
      kind: 'write',
    },
    {
      name: 'submit_evidence',
      signature:
        'submit_evidence(target_id: str, url: str)',
      description:
        'Attach a public HTTPS source after host validation.',
      kind: 'write',
    },
    {
      name: 'adjudicate',
      signature: 'adjudicate(target_id: str) → str',
      description:
        'Run comparative consensus and record the closed verdict.',
      kind: 'write',
    },
    {
      name: 'owner_clear_halt',
      signature:
        'owner_clear_halt(target_id: str)',
      description:
        'Owner-only recovery action for an active halt.',
      kind: 'write',
    },
    {
      name: 'is_halted',
      signature: 'is_halted(target_id: str) → bool',
      description:
        'Read whether a target is currently halted.',
      kind: 'read',
    },
    {
      name: 'read_case',
      signature: 'read_case(target_id: str) → str',
      description:
        'Read the stable JSON case record for the UI.',
      kind: 'read',
    },
  ],
};

const timeLabel = (iso: string) => {
  if (!iso) return '—';

  const date = new Date(iso);

  return `${date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })} · ${date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })}`;
};

function StatusBadge({ status }: { status: Status }) {
  const styles = {
    REGISTERED: 'border-slate-300 bg-slate-100 text-slate-600',
    EVIDENCE: 'border-amber-300 bg-amber-50 text-amber-700',
    ADJUDICATED: 'border-teal-300 bg-teal-50 text-teal-700',
  };

  return (
    <span
      data-testid={`status-${status.toLowerCase()}`}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-bold tracking-[.08em] ${styles[status]}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === 'EVIDENCE'
            ? 'bg-amber-500'
            : status === 'ADJUDICATED'
              ? 'bg-teal-600'
              : 'bg-slate-400'
        }`}
      />
      {status}
    </span>
  );
}

function VerdictBadge({ verdict }: { verdict: Verdict }) {
  if (!verdict) {
    return <span className="text-xs text-slate-400">Pending</span>;
  }

  const styles =
    verdict === 'CONFIRMED'
      ? 'border-red-300 bg-red-50 text-red-700'
      : verdict === 'CLEAR'
        ? 'border-teal-300 bg-teal-50 text-teal-700'
        : 'border-slate-300 bg-slate-100 text-slate-600';

  return (
    <span
      className={`rounded border px-2 py-1 text-[10px] font-bold tracking-[.08em] ${styles}`}
    >
      {verdict}
    </span>
  );
}

function Brand() {
  return (
    <Link
      href="/"
      className="sidebar-brand flex items-center gap-3 no-underline"
      data-testid="link-brand"
    >
      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-[#2cc5aa] text-[#122336] shadow-[0_0_0_3px_rgba(44,197,170,.14)]">
        <ShieldCheck size={21} strokeWidth={2.4} />
      </span>

      <span className="sidebar-copy min-w-0">
        <span className="font-display block text-[17px] font-bold tracking-[-.04em] text-[#f4f0e4]">
          HaltGate
        </span>
        <span className="mt-0.5 block font-mono-data text-[9px] uppercase tracking-[.16em] text-[#8495a8]">
          security console
        </span>
      </span>
    </Link>
  );
}

const navItems = [
  {
    href: '/',
    label: 'Overview',
    icon: LayoutDashboard,
  },
  {
    href: '/cases',
    label: 'Target cases',
    icon: ShieldAlert,
    count: '05',
  },
  {
    href: '/evidence',
    label: 'Evidence intake',
    icon: FileCode2,
  },
  {
    href: '/contract',
    label: 'Contract detail',
    icon: Code2,
  },
];

function Sidebar() {
  const [location] = useLocation();

  return (
    <aside className="sidebar">
      <Brand />

      <div className="sidebar-section mb-3 mt-11 px-3 font-mono-data text-[9px] uppercase tracking-[.18em] text-[#617388]">
        Operations
      </div>

      <nav
        className="sidebar-nav flex flex-1 flex-col gap-1"
        aria-label="Primary navigation"
      >
        {navItems.map(({ href, label, icon: Icon, count }) => {
          const active =
            href === '/'
              ? location === '/'
              : location.startsWith(href);

          return (
            <Link
              key={href}
              href={href}
              data-testid={`link-nav-${label
                .toLowerCase()
                .replace(' ', '-')}`}
              className={`nav-item group flex items-center gap-3 rounded-md px-3 py-2.5 text-[13px] font-semibold no-underline transition-colors ${
                active
                  ? 'active bg-[#243649] text-[#f5f1e7]'
                  : 'text-[#9aabbc] hover:bg-[#1c2d40] hover:text-[#e9eee8]'
              }`}
            >
              <Icon
                size={17}
                strokeWidth={active ? 2.3 : 1.8}
                className={
                  active ? 'text-[#43d1b5]' : 'text-[#70859a]'
                }
              />

              <span className="sidebar-label flex-1">{label}</span>

              {count && (
                <span className="nav-count rounded bg-[#304457] px-1.5 py-0.5 font-mono-data text-[9px] text-[#b4c3cf]">
                  {count}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-bottom border-t border-[#2a3a4b] pt-4">
        <div className="sidebar-footer-copy mb-3 px-3 font-mono-data text-[9px] uppercase tracking-[.16em] text-[#617388]">
          Canonical plane
        </div>

        <div className="flex items-center gap-2 rounded-md bg-[#1a2a3b] p-2.5">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#3dd2b5] opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-[#3dd2b5]" />
          </span>

          <span className="sidebar-footer-copy font-mono-data text-[10px] text-[#b5c5d1]">
            STUDIONET LIVE
          </span>
        </div>

        <div className="sidebar-footer-copy mt-3 px-3 font-mono-data text-[9px] leading-relaxed text-[#617388]">
          Demo surface · writes are simulated locally
        </div>
      </div>
    </aside>
  );
}

function Topbar() {
  const [location] = useLocation();

  const title =
    location === '/'
      ? 'Operations overview'
      : location === '/cases'
        ? 'Target cases'
        : location === '/evidence'
          ? 'Evidence intake'
          : 'Canonical contract';

  return (
    <header className="topbar">
      <div className="flex min-w-0 items-center gap-3">
        <div className="hidden rounded border border-[#d4d4c7] bg-[#f4f1e8] p-1.5 sm:block">
          <Radio size={14} className="text-[#158c78]" />
        </div>

        <div className="min-w-0">
          <div className="font-display truncate text-[15px] font-semibold tracking-[-.02em]">
            {title}
          </div>

          <div className="font-mono-data mt-0.5 hidden text-[10px] uppercase tracking-[.13em] text-slate-500 sm:block">
            GenLayer protocol / canonical decision plane
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        <span className="hidden items-center gap-2 rounded-full border border-[#cddbd3] bg-[#eef6f0] px-3 py-1.5 text-[11px] font-semibold text-[#23735f] sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-[#2cad8d]" />
          Live read-only feed
        </span>

        <button
          type="button"
          aria-label="Refresh activity"
          data-testid="button-refresh"
          className="rounded-md border border-[#d8d5c9] bg-[#faf8f1] p-2 text-slate-600 transition hover:border-[#79b5a8] hover:text-[#147e6d]"
        >
          <RefreshCw size={15} />
        </button>

        <div
          className="grid h-8 w-8 place-items-center rounded-full bg-[#d8e4df] font-mono-data text-[10px] font-medium text-[#236756]"
          title="Operator identity"
        >
          OP
        </div>
      </div>
    </header>
  );
}

function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="main-area">
        <Topbar />
        {children}
      </div>
    </div>
  );
}

function SectionHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        <div className="mb-2 flex items-center gap-2 font-mono-data text-[10px] font-medium uppercase tracking-[.17em] text-[#148773]">
          <span className="h-px w-5 bg-[#36bca4]" />
          {eyebrow}
        </div>

        <h1 className="font-display text-[clamp(25px,3vw,34px)] font-bold leading-[1.05] tracking-[-.055em] text-[#1b2a3c]">
          {title}
        </h1>

        {description && (
          <p className="mt-2 max-w-2xl text-[13px] leading-relaxed text-slate-500">
            {description}
          </p>
        )}
      </div>

      {action}
    </div>
  );
}

function StatCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = 'default',
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Activity;
  tone?: 'default' | 'danger' | 'amber' | 'teal';
}) {
  const color =
    tone === 'danger'
      ? 'text-red-700 bg-red-50 border-red-200'
      : tone === 'amber'
        ? 'text-amber-700 bg-amber-50 border-amber-200'
        : tone === 'teal'
          ? 'text-teal-700 bg-teal-50 border-teal-200'
          : 'text-slate-600 bg-slate-100 border-slate-200';

  return (
    <div className="panel panel-hover p-4">
      <div className="flex items-start justify-between">
        <div className="font-mono-data text-[10px] uppercase tracking-[.13em] text-slate-500">
          {label}
        </div>

        <span className={`rounded-md border p-1.5 ${color}`}>
          <Icon size={15} />
        </span>
      </div>

      <div className="mt-4 flex items-end justify-between">
        <div className="font-display text-[31px] font-bold leading-none tracking-[-.06em]">
          {value}
        </div>

        <div className="max-w-[130px] text-right text-[11px] leading-snug text-slate-500"> **…**

_This response is too long to display in full._
