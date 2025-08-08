import React, { useEffect, useState, useRef } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import {
  getOpportunitiesForConsultant,
  updateOpportunityStatus,
  loadOpportunities,
  type Opportunity,
} from "@/services/opportunityStore";

// CSV export helper
const exportToCSV = (data: Opportunity[], filename = "my_opportunities.csv") => {
  const csvRows = [
    ["Title", "Description", "Start Date", "End Date", "Status"],
    ...data.map((opp) => [
      opp.title,
      opp.description,
      opp.startDate,
      opp.endDate,
      opp.status,
    ]),
  ];
  const csvContent = csvRows.map((e) => e.join(",")).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

const ConsultantOpportunities: React.FC = () => {
  const { user } = useAuth();
  const [myOpportunities, setMyOpportunities] = useState<Opportunity[]>([]);
  const [newOpportunities, setNewOpportunities] = useState<Opportunity[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState<"title" | "status">("title");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [declineReason, setDeclineReason] = useState("");
  const [declineId, setDeclineId] = useState<string | null>(null);
  const [statusLog, setStatusLog] = useState<Record<string, string[]>>({});
  const [notification, setNotification] = useState<string | null>(null);
  const prevIds = useRef<Set<string>>(new Set());

  // Work status and files per opportunity
  const [workStatusMap, setWorkStatusMap] = useState<Record<string, string>>({});
  const [workFiles, setWorkFiles] = useState<Record<string, File | null>>({});

  const refreshOpportunities = () => {
    if (user?.email) {
      loadOpportunities();
      const allOpps = getOpportunitiesForConsultant(user.email);
      setMyOpportunities(allOpps);

      // Detect new opportunities
      const currentIds = new Set(allOpps.map((o) => o.id));
      const prev = prevIds.current;
      const newOnes = allOpps.filter((o) => !prev.has(o.id) && o.status === "pending");
      if (newOnes.length > 0) {
        setNewOpportunities((prevNew) => [...prevNew, ...newOnes]);
        setNotification("You have new opportunity assignments!");
      }
      prevIds.current = currentIds;
    }
  };

  useEffect(() => {
    refreshOpportunities();
  }, [user]);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handleResponse = (id: string, status: "accepted" | "declined", reason?: string) => {
    updateOpportunityStatus(id, status);

    setStatusLog((prev) => ({
      ...prev,
      [id]: [
        ...(prev[id] || []),
        `Status changed to ${status}${reason ? ` (Reason: ${reason})` : ""} at ${new Date().toLocaleString()}`,
      ],
    }));

    // Remove from new opportunities
    setNewOpportunities((prev) => prev.filter((o) => o.id !== id));

    refreshOpportunities();
  };

  const handleWorkSubmit = (e: React.FormEvent, oppId: string) => {
    e.preventDefault();
    const file = workFiles[oppId];
    const status = workStatusMap[oppId];
    if (!file || !status) return;

    setStatusLog((prev) => ({
      ...prev,
      [oppId]: [
        ...(prev[oppId] || []),
        `Work file uploaded (${file.name}) and status updated to "${status}" at ${new Date().toLocaleString()}`,
      ],
    }));

    setWorkFiles((prev) => ({ ...prev, [oppId]: null }));
    setWorkStatusMap((prev) => ({ ...prev, [oppId]: "" }));
  };

  // Performance stats
  const totalAssigned = myOpportunities.length;
  const responseRate = totalAssigned > 0
    ? ((Object.keys(statusLog).length / totalAssigned) * 100).toFixed(1)
    : "0";
  const completionRate = totalAssigned > 0
    ? ((myOpportunities.filter((o) => o.status === "accepted").length / totalAssigned) * 100).toFixed(1)
    : "0";
  const engagementRate = totalAssigned > 0
    ? ((myOpportunities.filter((o) => o.status !== "pending").length / totalAssigned) * 100).toFixed(1)
    : "0";

  // Filter and sort
  const filtered = [...myOpportunities]
    .filter(
      (opp) =>
        (!search ||
          opp.title.toLowerCase().includes(search.toLowerCase()) ||
          opp.description.toLowerCase().includes(search.toLowerCase())) &&
        (!statusFilter || opp.status === statusFilter)
    )
    .sort((a, b) => {
      let valA = a[sortBy];
      let valB = b[sortBy];
      if (valA < valB) return sortDir === "asc" ? -1 : 1;
      if (valA > valB) return sortDir === "asc" ? 1 : -1;
      return 0;
    });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge variant="outline">Pending</Badge>;
      case "accepted":
        return <Badge className="bg-green-500">Accepted</Badge>;
      case "declined":
        return <Badge variant="destructive">Declined</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  const renderOpportunityCard = (opp: Opportunity) => (
    <Card key={opp.id}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{opp.title}</CardTitle>
          {getStatusBadge(opp.status)}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm mb-4">{opp.description}</p>
        <p className="text-xs text-muted-foreground mb-2">
          Start: <strong>{opp.startDate || "-"}</strong> | End: <strong>{opp.endDate || "-"}</strong>
        </p>
        {opp.status === "pending" && (
          <div className="flex gap-2">
            <Button onClick={() => handleResponse(opp.id, "accepted")} className="bg-green-600 hover:bg-green-700">Accept</Button>
            <Button variant="outline" onClick={() => setDeclineId(opp.id)}>Decline</Button>
          </div>
        )}
        {opp.status === "accepted" && (
          <form onSubmit={(e) => handleWorkSubmit(e, opp.id)} className="mt-3 space-y-2">
            <Input type="file" onChange={e => setWorkFiles(prev => ({ ...prev, [opp.id]: e.target.files?.[0] || null }))} required />
            <Input placeholder="Enter work status" value={workStatusMap[opp.id] || ""} onChange={e => setWorkStatusMap(prev => ({ ...prev, [opp.id]: e.target.value }))} required />
            <Button type="submit" size="sm" disabled={!workFiles[opp.id] || !workStatusMap[opp.id]}>Submit Work</Button>
          </form>
        )}
        {opp.status !== "pending" && opp.status !== "accepted" && (
          <p className="text-xs text-muted-foreground">You have {opp.status} this opportunity.</p>
        )}
        {statusLog[opp.id] && (
          <div className="mt-2">
            <p className="text-xs font-semibold">History:</p>
            <ul className="text-xs list-disc list-inside">
              {statusLog[opp.id].map((log, idx) => (
                <li key={idx}>{log}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="p-6 space-y-6">
      {notification && (
        <div className="bg-green-100 border border-green-400 text-green-800 px-4 py-2 rounded mb-4">
          {notification}
        </div>
      )}

      <div>
        <h2 className="text-2xl font-bold">My Opportunities</h2>
        <p className="text-muted-foreground text-sm">
          Review and respond to opportunities assigned to you
        </p>
      </div>

      {user && (
        <div className="text-sm font-medium">
          Consultant ID: <span className="font-mono">{user.id}</span>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card><CardContent className="p-4"><div className="text-lg font-bold">{totalAssigned}</div><p className="text-sm">Opportunities Provided</p></CardContent></Card>
        <Card><CardContent className="p-4"><div className="text-lg font-bold">{responseRate}%</div><p className="text-sm">Response Rate</p></CardContent></Card>
        <Card><CardContent className="p-4"><div className="text-lg font-bold">{completionRate}%</div><p className="text-sm">Completion Rate</p></CardContent></Card>
        <Card><CardContent className="p-4"><div className="text-lg font-bold">{engagementRate}%</div><p className="text-sm">Engagement Rate</p></CardContent></Card>
      </div>

      {/* New Opportunities */}
      {newOpportunities.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-primary">New Opportunities</h3>
          <div className="space-y-4 mt-2">
            {newOpportunities.map(renderOpportunityCard)}
          </div>
        </div>
      )}

      {/* Search, Filter, Sort */}
      <div className="flex flex-wrap gap-2 items-center mb-2">
        <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="w-56" />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="declined">Declined</option>
        </select>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value as "title" | "status")} className="border rounded px-2 py-1">
          <option value="title">Sort by Title</option>
          <option value="status">Sort by Status</option>
        </select>
        <select value={sortDir} onChange={(e) => setSortDir(e.target.value as "asc" | "desc")} className="border rounded px-2 py-1">
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
        <Button size="sm" variant="outline" onClick={() => exportToCSV(filtered)}>Export CSV</Button>
      </div>

      {/* All Opportunities */}
      <div>
        <h3 className="text-lg font-semibold">All Opportunities</h3>
        {filtered.length === 0 ? (
          <Card><CardContent className="py-8 text-center"><p className="text-muted-foreground">No opportunities assigned yet.</p></CardContent></Card>
        ) : (
          <div className="space-y-4">
            {filtered.map(renderOpportunityCard)}
          </div>
        )}
      </div>

      {/* Decline Modal */}
      {declineId && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-2">Decline Opportunity</h3>
            <p className="mb-2 text-sm">Please provide a reason for declining:</p>
            <Input value={declineReason} onChange={(e) => setDeclineReason(e.target.value)} className="mb-2" />
            <div className="flex gap-2 mt-2">
              <Button size="sm" variant="destructive" onClick={() => { handleResponse(declineId, "declined", declineReason); setDeclineId(null); setDeclineReason(""); }} disabled={!declineReason}>Submit</Button>
              <Button size="sm" variant="outline" onClick={() => { setDeclineId(null); setDeclineReason(""); }}>Cancel</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsultantOpportunities;
