CREATE TABLE IF NOT EXISTS master_agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'domain',
    status TEXT NOT NULL DEFAULT 'idle',
    description TEXT,
    config_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS task_queue (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    master_id TEXT NOT NULL,
    specialist_id TEXT,
    orchestrator_master_id TEXT,
    objective TEXT NOT NULL,
    display_name TEXT,
    context TEXT DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'P2',
    status TEXT NOT NULL DEFAULT 'pending',
    execution_stage TEXT NOT NULL DEFAULT 'planned',
    result TEXT,
    error_ref TEXT,
    parent_task_id TEXT,
    program_id TEXT,
    application_id TEXT,
    idempotency_key TEXT,
    correlation_id TEXT,
    delegation_schema_version TEXT,
    result_schema_version TEXT,
    compression_ratio REAL,
    last_model_tier TEXT,
    archived INTEGER NOT NULL DEFAULT 0,
    archived_reason TEXT,
    archived_at TEXT,
    assigned_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (master_id) REFERENCES master_agents(id),
    FOREIGN KEY (parent_task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS task_board_meta (
    task_id TEXT PRIMARY KEY,
    release_version TEXT NOT NULL DEFAULT 'v1',
    phase_hint TEXT DEFAULT '',
    card_rank REAL NOT NULL DEFAULT 0,
    labels_json TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS task_transition_history (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT NOT NULL,
    from_execution_stage TEXT,
    to_execution_stage TEXT NOT NULL,
    release_version TEXT,
    actor_agent_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    decision_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS task_hygiene_runs (
    id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS task_hygiene_events (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES task_hygiene_runs(id),
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS error_log (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    source TEXT NOT NULL,
    error_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'error',
    message TEXT NOT NULL,
    stack_trace TEXT,
    context_json TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'open',
    assigned_to TEXT DEFAULT 'engineer',
    resolution TEXT,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS execution_history (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    agent_id TEXT NOT NULL,
    task_id TEXT,
    action TEXT NOT NULL,
    input_summary TEXT,
    outcome TEXT NOT NULL,
    output_summary TEXT,
    duration_seconds REAL,
    model_used TEXT,
    token_count INTEGER
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS autonomy_runs (
    id TEXT PRIMARY KEY,
    trigger_source TEXT NOT NULL,
    actor_agent_id TEXT NOT NULL,
    requested_mode TEXT NOT NULL,
    credential_class TEXT NOT NULL,
    host_id TEXT NOT NULL,
    repo_ids_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'running',
    validation_status TEXT NOT NULL DEFAULT 'pending',
    commit_anchor TEXT DEFAULT '{}',
    rollback_anchor TEXT DEFAULT '{}',
    quarantine_status TEXT NOT NULL DEFAULT 'clear',
    quarantine_reason TEXT DEFAULT '',
    bootstrap_report_json TEXT NOT NULL DEFAULT '{}',
    error_detail TEXT DEFAULT '',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS autonomy_actions (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    repo_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    planned_action TEXT NOT NULL,
    credential_ref TEXT DEFAULT '',
    credential_class TEXT NOT NULL,
    requested_mode TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    validation_status TEXT NOT NULL DEFAULT 'pending',
    commit_anchor TEXT DEFAULT '',
    rollback_anchor TEXT DEFAULT '{}',
    quarantine_status TEXT NOT NULL DEFAULT 'clear',
    quarantine_reason TEXT DEFAULT '',
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES autonomy_runs(id)
);

CREATE TABLE IF NOT EXISTS autonomy_repo_sync (
    repo_id TEXT PRIMARY KEY,
    classification TEXT NOT NULL,
    local_path TEXT NOT NULL,
    expected_primary_remote TEXT NOT NULL,
    effective_primary_remote TEXT NOT NULL,
    autonomy_scope TEXT NOT NULL,
    allowed_modes_json TEXT NOT NULL DEFAULT '[]',
    preflight_only INTEGER NOT NULL DEFAULT 0,
    wave INTEGER NOT NULL DEFAULT 1,
    manifest_stage TEXT NOT NULL DEFAULT '',
    manifest_sync_status TEXT NOT NULL DEFAULT 'pending',
    last_run_id TEXT DEFAULT '',
    last_status TEXT NOT NULL DEFAULT 'never_run',
    last_validation_status TEXT NOT NULL DEFAULT 'pending',
    last_commit_anchor TEXT DEFAULT '',
    last_rollback_anchor TEXT DEFAULT '{}',
    last_provenance_id TEXT DEFAULT '',
    quarantine_status TEXT NOT NULL DEFAULT 'clear',
    quarantine_reason TEXT DEFAULT '',
    last_synced_at TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS deployment_provenance (
    id TEXT PRIMARY KEY,
    repo_id TEXT NOT NULL,
    autonomy_run_id TEXT DEFAULT '',
    source TEXT NOT NULL DEFAULT 'autonomy',
    deploy_target TEXT NOT NULL,
    ref_name TEXT DEFAULT '',
    commit_sha TEXT DEFAULT '',
    rollback_anchor TEXT DEFAULT '{}',
    validation_status TEXT NOT NULL DEFAULT 'pending',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS program_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL,
    owner_master_id TEXT NOT NULL,
    repo_path TEXT NOT NULL,
    repo_remote TEXT DEFAULT '',
    stack TEXT NOT NULL,
    app_status TEXT NOT NULL DEFAULT 'active',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (owner_master_id) REFERENCES master_agents(id)
);

CREATE TABLE IF NOT EXISTS data_store_registry (
    id TEXT PRIMARY KEY,
    program_id TEXT NOT NULL,
    name TEXT NOT NULL,
    engine TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'app_primary',
    location TEXT NOT NULL,
    env_keys TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'unknown',
    last_verified_at TEXT,
    notes TEXT DEFAULT '',
    FOREIGN KEY (program_id) REFERENCES program_registry(id)
);

CREATE TABLE IF NOT EXISTS agent_program_assignments (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    program_id TEXT NOT NULL,
    responsibility TEXT NOT NULL DEFAULT 'owner',
    priority TEXT NOT NULL DEFAULT 'P2',
    status TEXT NOT NULL DEFAULT 'active',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(agent_id, program_id),
    FOREIGN KEY (agent_id) REFERENCES master_agents(id),
    FOREIGN KEY (program_id) REFERENCES program_registry(id)
);

CREATE TABLE IF NOT EXISTS prompt_assets_registry (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS application_registry (
    id TEXT PRIMARY KEY,
    program_id TEXT NOT NULL,
    name TEXT NOT NULL,
    owner_master_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'placeholder',
    kind TEXT NOT NULL DEFAULT 'placeholder',
    repo_path TEXT NOT NULL,
    frontend_entry TEXT DEFAULT '',
    backend_entry TEXT DEFAULT '',
    dev_url TEXT DEFAULT '',
    live_url TEXT DEFAULT '',
    staging_url TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (program_id) REFERENCES program_registry(id),
    FOREIGN KEY (owner_master_id) REFERENCES master_agents(id)
);

CREATE TABLE IF NOT EXISTS agent_context_limits (
    agent_id TEXT PRIMARY KEY,
    context_limit_tokens INTEGER NOT NULL,
    warning_threshold REAL NOT NULL DEFAULT 0.8,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS task_catalog_runs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    task_template_id TEXT NOT NULL,
    objective TEXT NOT NULL,
    priority TEXT NOT NULL,
    planned_agents_json TEXT NOT NULL,
    queued_task_ids_json TEXT NOT NULL,
    requested_by TEXT NOT NULL DEFAULT 'system'
);

CREATE TABLE IF NOT EXISTS chat_threads (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    execution_mode TEXT NOT NULL DEFAULT 'free_reasoning',
    default_model_profile_id TEXT,
    override_model_profile_id TEXT,
    continuation_from_thread_id TEXT,
    primary_task_id TEXT,
    context_refresh_count INTEGER NOT NULL DEFAULT 0,
    program_id TEXT,
    created_by TEXT NOT NULL DEFAULT 'system',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_message_at TEXT,
    FOREIGN KEY (continuation_from_thread_id) REFERENCES chat_threads(id)
);

CREATE TABLE IF NOT EXISTS task_thread_bindings (
    task_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL UNIQUE,
    sync_titles INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id)
);

CREATE TABLE IF NOT EXISTS context_nodes (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    path_or_ref TEXT NOT NULL,
    label TEXT DEFAULT '',
    hash TEXT DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(kind, path_or_ref)
);

CREATE TABLE IF NOT EXISTS task_context_links (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    link_type TEXT NOT NULL DEFAULT 'reference',
    required INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'engineer',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(task_id, node_id, link_type),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (node_id) REFERENCES context_nodes(id)
);

CREATE TABLE IF NOT EXISTS memory_deltas (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    memory_file TEXT NOT NULL,
    summary TEXT NOT NULL,
    links_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'posted',
    meta_json TEXT DEFAULT '{}',
    program_id TEXT,
    application_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id)
);

CREATE TABLE IF NOT EXISTS chat_task_links (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id),
    FOREIGN KEY (message_id) REFERENCES chat_messages(id),
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS task_cost_ledger (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    program_id TEXT,
    application_id TEXT,
    source_message_id TEXT,
    model_name TEXT,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0,
    allocation_method TEXT NOT NULL DEFAULT 'equal_split_turn',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (program_id) REFERENCES program_registry(id),
    FOREIGN KEY (application_id) REFERENCES application_registry(id),
    FOREIGN KEY (source_message_id) REFERENCES chat_messages(id)
);

CREATE TABLE IF NOT EXISTS chat_thread_carryovers (
    id TEXT PRIMARY KEY,
    from_thread_id TEXT NOT NULL,
    to_thread_id TEXT NOT NULL,
    carryover_packet_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (from_thread_id) REFERENCES chat_threads(id),
    FOREIGN KEY (to_thread_id) REFERENCES chat_threads(id)
);

CREATE TABLE IF NOT EXISTS agent_libraries (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    name TEXT NOT NULL,
    rel_path TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(agent_id, rel_path)
);

CREATE TABLE IF NOT EXISTS chat_thread_libraries (
    thread_id TEXT NOT NULL,
    library_id TEXT NOT NULL,
    preload_state TEXT NOT NULL DEFAULT 'pending',
    preload_tokens INTEGER NOT NULL DEFAULT 0,
    preload_error TEXT,
    preloaded_at TEXT,
    selected_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (thread_id, library_id),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id),
    FOREIGN KEY (library_id) REFERENCES agent_libraries(id)
);

CREATE TABLE IF NOT EXISTS chat_message_file_refs (
    id TEXT PRIMARY KEY,
    message_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    ref_scope TEXT NOT NULL,
    rel_path TEXT NOT NULL,
    resolved_path TEXT NOT NULL,
    tokens INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (message_id) REFERENCES chat_messages(id),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id)
);

CREATE TABLE IF NOT EXISTS agent_memory_entries (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    entry_type TEXT NOT NULL DEFAULT 'session_commit',
    summary TEXT NOT NULL,
    source_message_ids_json TEXT NOT NULL DEFAULT '[]',
    memory_file_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id)
);

CREATE TABLE IF NOT EXISTS orchestration_flows (
    id TEXT PRIMARY KEY,
    owner_agent_id TEXT NOT NULL,
    program_id TEXT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    execution_mode TEXT NOT NULL DEFAULT 'locked_pipeline',
    schedule_kind TEXT NOT NULL DEFAULT 'placeholder',
    schedule_expr TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    created_by TEXT NOT NULL DEFAULT 'system',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (program_id) REFERENCES program_registry(id)
);

CREATE TABLE IF NOT EXISTS orchestration_flow_steps (
    id TEXT PRIMARY KEY,
    flow_id TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    agent_id TEXT NOT NULL,
    objective_template TEXT NOT NULL,
    input_contract_json TEXT NOT NULL DEFAULT '{}',
    output_schema_json TEXT NOT NULL DEFAULT '{}',
    retry_policy_json TEXT NOT NULL DEFAULT '{}',
    on_failure TEXT NOT NULL DEFAULT 'escalate',
    timeout_seconds INTEGER NOT NULL DEFAULT 120,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(flow_id, step_order),
    FOREIGN KEY (flow_id) REFERENCES orchestration_flows(id)
);

CREATE TABLE IF NOT EXISTS orchestration_flow_runs (
    id TEXT PRIMARY KEY,
    flow_id TEXT NOT NULL,
    trigger_type TEXT NOT NULL DEFAULT 'manual',
    triggered_by TEXT NOT NULL DEFAULT 'system',
    status TEXT NOT NULL DEFAULT 'queued',
    root_thread_id TEXT,
    root_task_id TEXT,
    run_context_json TEXT NOT NULL DEFAULT '{}',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (flow_id) REFERENCES orchestration_flows(id),
    FOREIGN KEY (root_thread_id) REFERENCES chat_threads(id),
    FOREIGN KEY (root_task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS orchestration_flow_run_steps (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    task_id TEXT,
    status TEXT NOT NULL DEFAULT 'queued',
    output_valid INTEGER NOT NULL DEFAULT 0,
    result_packet_id TEXT,
    escalation_id TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(run_id, step_id),
    FOREIGN KEY (run_id) REFERENCES orchestration_flow_runs(id),
    FOREIGN KEY (step_id) REFERENCES orchestration_flow_steps(id),
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE TABLE IF NOT EXISTS task_flow_locks (
    task_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    locked_agent_id TEXT NOT NULL,
    output_schema_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (run_id) REFERENCES orchestration_flow_runs(id),
    FOREIGN KEY (step_id) REFERENCES orchestration_flow_steps(id)
);

CREATE TABLE IF NOT EXISTS agent_controls (
    agent_id TEXT PRIMARY KEY,
    autonomous_sync INTEGER NOT NULL DEFAULT 1,
    require_schema_approval INTEGER NOT NULL DEFAULT 1,
    debug_mode INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS specialist_agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    agent_kind TEXT NOT NULL,
    owner_master_id TEXT NOT NULL,
    parent_agent_id TEXT NOT NULL,
    program_id TEXT,
    application_id TEXT,
    task_slug TEXT,
    prompt_agent_key TEXT,
    source_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    chat_enabled INTEGER NOT NULL DEFAULT 1,
    delegation_enabled INTEGER NOT NULL DEFAULT 1,
    allow_write_tools INTEGER NOT NULL DEFAULT 0,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (owner_master_id) REFERENCES master_agents(id),
    FOREIGN KEY (program_id) REFERENCES program_registry(id),
    FOREIGN KEY (application_id) REFERENCES application_registry(id)
);

CREATE TABLE IF NOT EXISTS specialist_tool_bindings (
    id TEXT PRIMARY KEY,
    specialist_id TEXT NOT NULL,
    tool_key TEXT NOT NULL,
    provider TEXT NOT NULL,
    display_name TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'read_only',
    writes_enabled INTEGER NOT NULL DEFAULT 0,
    required_env_keys TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'unknown',
    config_json TEXT DEFAULT '{}',
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(specialist_id, tool_key),
    FOREIGN KEY (specialist_id) REFERENCES specialist_agents(id)
);

CREATE TABLE IF NOT EXISTS master_specialist_routing_rules (
    id TEXT PRIMARY KEY,
    master_id TEXT NOT NULL,
    program_id TEXT NOT NULL,
    pattern TEXT NOT NULL,
    target_specialist_id TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (master_id) REFERENCES master_agents(id),
    FOREIGN KEY (program_id) REFERENCES program_registry(id),
    FOREIGN KEY (target_specialist_id) REFERENCES specialist_agents(id)
);

CREATE TABLE IF NOT EXISTS specialist_invocations (
    id TEXT PRIMARY KEY,
    specialist_id TEXT NOT NULL,
    tool_key TEXT NOT NULL,
    action TEXT NOT NULL,
    mode TEXT NOT NULL,
    request_json TEXT NOT NULL,
    response_json TEXT,
    success INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    duration_ms INTEGER,
    task_id TEXT,
    thread_id TEXT,
    message_id TEXT,
    actor_agent_id TEXT,
    invocation_scope TEXT,
    correlation_id TEXT,
    model_provider TEXT,
    model_name TEXT,
    program_id TEXT,
    application_id TEXT,
    decision_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (specialist_id) REFERENCES specialist_agents(id),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id),
    FOREIGN KEY (message_id) REFERENCES chat_messages(id)
);

CREATE TABLE IF NOT EXISTS workspace_project_usage_daily (
    id TEXT PRIMARY KEY,
    date_key TEXT NOT NULL,
    program_id TEXT NOT NULL,
    application_id TEXT,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(date_key, program_id, application_id),
    FOREIGN KEY (program_id) REFERENCES program_registry(id),
    FOREIGN KEY (application_id) REFERENCES application_registry(id)
);

CREATE TABLE IF NOT EXISTS specialist_execution_policies (
    specialist_id TEXT PRIMARY KEY,
    max_retries INTEGER NOT NULL DEFAULT 3,
    timeout_seconds INTEGER NOT NULL DEFAULT 120,
    max_concurrency INTEGER NOT NULL DEFAULT 1,
    escalation_master_id TEXT NOT NULL DEFAULT 'engineer',
    allow_master_direct_execution INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (specialist_id) REFERENCES specialist_agents(id)
);

CREATE TABLE IF NOT EXISTS task_result_packets (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    specialist_id TEXT NOT NULL,
    schema_version TEXT NOT NULL DEFAULT '1.0',
    status TEXT NOT NULL,
    map_summaries_json TEXT NOT NULL,
    reduce_summary TEXT NOT NULL,
    outputs_json TEXT NOT NULL,
    verification_json TEXT NOT NULL,
    next_actions_json TEXT NOT NULL DEFAULT '[]',
    token_usage_json TEXT NOT NULL DEFAULT '{}',
    correlation_id TEXT,
    compression_ratio REAL,
    compression_meta_json TEXT NOT NULL DEFAULT '{}',
    contract_warnings_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (specialist_id) REFERENCES specialist_agents(id)
);

CREATE TABLE IF NOT EXISTS task_escalations (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    specialist_id TEXT NOT NULL,
    escalation_master_id TEXT NOT NULL DEFAULT 'engineer',
    blocker_type TEXT NOT NULL,
    blocker_summary TEXT NOT NULL,
    attempted_actions_json TEXT NOT NULL,
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    recommended_next_owner TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'error',
    correlation_id TEXT,
    contract_warnings_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'open',
    resolution TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (specialist_id) REFERENCES specialist_agents(id)
);

CREATE TABLE IF NOT EXISTS artisan_wp_inventory_snapshots (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'ok',
    snapshot_json TEXT NOT NULL,
    checked_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_task_queue_master ON task_queue(master_id, status);
CREATE INDEX IF NOT EXISTS idx_task_queue_priority ON task_queue(priority, status);
CREATE INDEX IF NOT EXISTS idx_task_queue_parent ON task_queue(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_task_queue_program_status_stage ON task_queue(program_id, status, execution_stage, created_at);
CREATE INDEX IF NOT EXISTS idx_error_log_status ON error_log(status, severity);
CREATE INDEX IF NOT EXISTS idx_error_log_source ON error_log(source);
CREATE INDEX IF NOT EXISTS idx_execution_history_agent ON execution_history(agent_id, created_at);
CREATE INDEX IF NOT EXISTS idx_execution_history_task ON execution_history(task_id);
CREATE INDEX IF NOT EXISTS idx_autonomy_runs_created ON autonomy_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_autonomy_runs_status ON autonomy_runs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_autonomy_actions_run ON autonomy_actions(run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_autonomy_actions_repo ON autonomy_actions(repo_id, created_at);
CREATE INDEX IF NOT EXISTS idx_deployment_provenance_repo ON deployment_provenance(repo_id, created_at);
CREATE INDEX IF NOT EXISTS idx_program_registry_owner ON program_registry(owner_master_id, app_status);
CREATE INDEX IF NOT EXISTS idx_data_store_registry_program ON data_store_registry(program_id, role, status);
CREATE INDEX IF NOT EXISTS idx_agent_program_assignments_agent ON agent_program_assignments(agent_id, status);
CREATE INDEX IF NOT EXISTS idx_agent_program_assignments_program ON agent_program_assignments(program_id, status);
CREATE INDEX IF NOT EXISTS idx_prompt_assets_agent ON prompt_assets_registry(agent_id, asset_type, status);
CREATE INDEX IF NOT EXISTS idx_application_registry_program_status ON application_registry(program_id, status);
CREATE INDEX IF NOT EXISTS idx_application_registry_owner_status ON application_registry(owner_master_id, status);
CREATE INDEX IF NOT EXISTS idx_task_catalog_runs_created_at ON task_catalog_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_task_catalog_runs_template ON task_catalog_runs(task_template_id, priority);
CREATE INDEX IF NOT EXISTS idx_chat_threads_agent_status ON chat_threads(agent_id, status, updated_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_thread_created ON chat_messages(thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role_created ON chat_messages(role, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_task_links_thread_task ON chat_task_links(thread_id, task_id);
CREATE INDEX IF NOT EXISTS idx_task_cost_ledger_task_created ON task_cost_ledger(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_cost_ledger_program_created ON task_cost_ledger(program_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_cost_ledger_application_created ON task_cost_ledger(application_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_carryovers_from_thread ON chat_thread_carryovers(from_thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_carryovers_to_thread ON chat_thread_carryovers(to_thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_thread_bindings_thread ON task_thread_bindings(thread_id);
CREATE INDEX IF NOT EXISTS idx_agent_libraries_agent ON agent_libraries(agent_id, status, updated_at);
CREATE INDEX IF NOT EXISTS idx_chat_thread_libraries_thread ON chat_thread_libraries(thread_id, selected_at);
CREATE INDEX IF NOT EXISTS idx_chat_thread_libraries_library ON chat_thread_libraries(library_id, selected_at);
CREATE INDEX IF NOT EXISTS idx_chat_message_file_refs_thread ON chat_message_file_refs(thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_message_file_refs_message ON chat_message_file_refs(message_id);
CREATE INDEX IF NOT EXISTS idx_agent_memory_entries_agent ON agent_memory_entries(agent_id, created_at);
CREATE INDEX IF NOT EXISTS idx_agent_memory_entries_thread ON agent_memory_entries(thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_orch_flows_owner ON orchestration_flows(owner_agent_id, status, updated_at);
CREATE INDEX IF NOT EXISTS idx_orch_flows_program ON orchestration_flows(program_id, status, updated_at);
CREATE INDEX IF NOT EXISTS idx_orch_flow_steps_flow ON orchestration_flow_steps(flow_id, step_order);
CREATE INDEX IF NOT EXISTS idx_orch_flow_runs_flow ON orchestration_flow_runs(flow_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_orch_flow_runs_root_thread ON orchestration_flow_runs(root_thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_orch_flow_run_steps_run ON orchestration_flow_run_steps(run_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_orch_flow_run_steps_task ON orchestration_flow_run_steps(task_id);
CREATE INDEX IF NOT EXISTS idx_task_flow_locks_run ON task_flow_locks(run_id, step_id, created_at);
CREATE INDEX IF NOT EXISTS idx_context_nodes_kind_ref ON context_nodes(kind, path_or_ref);
CREATE INDEX IF NOT EXISTS idx_task_context_links_task ON task_context_links(task_id, required, updated_at);
CREATE INDEX IF NOT EXISTS idx_task_context_links_node ON task_context_links(node_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_memory_deltas_task ON memory_deltas(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_memory_deltas_agent ON memory_deltas(agent_id, created_at);
CREATE INDEX IF NOT EXISTS idx_agent_controls_updated ON agent_controls(updated_at);
CREATE INDEX IF NOT EXISTS idx_specialist_agents_owner_status ON specialist_agents(owner_master_id, status);
CREATE INDEX IF NOT EXISTS idx_specialist_agents_program_status ON specialist_agents(program_id, status);
CREATE INDEX IF NOT EXISTS idx_specialist_agents_kind_status ON specialist_agents(agent_kind, status);
CREATE INDEX IF NOT EXISTS idx_specialist_tool_bindings_specialist ON specialist_tool_bindings(specialist_id, status);
CREATE INDEX IF NOT EXISTS idx_master_specialist_rules_lookup ON master_specialist_routing_rules(master_id, program_id, status, priority);
CREATE INDEX IF NOT EXISTS idx_specialist_invocations_specialist ON specialist_invocations(specialist_id, created_at);
CREATE INDEX IF NOT EXISTS idx_specialist_invocations_task ON specialist_invocations(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_result_packets_task ON task_result_packets(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_escalations_task ON task_escalations(task_id, status);
CREATE INDEX IF NOT EXISTS idx_task_escalations_correlation ON task_escalations(correlation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_board_meta_release ON task_board_meta(release_version, updated_at);
CREATE INDEX IF NOT EXISTS idx_task_transition_history_task ON task_transition_history(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_hygiene_events_task ON task_hygiene_events(task_id, created_at);
CREATE INDEX IF NOT EXISTS idx_artisan_wp_inventory_checked_at ON artisan_wp_inventory_snapshots(checked_at);
CREATE INDEX IF NOT EXISTS idx_workspace_project_usage_day_program ON workspace_project_usage_daily(date_key, program_id);
CREATE INDEX IF NOT EXISTS idx_workspace_project_usage_program_day ON workspace_project_usage_daily(program_id, date_key);

INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('default_model_provider', 'claude', 'Default model provider for orchestration routing'),
    ('default_model', 'sonnet', 'Default Claude model for all agents'),
    ('default_model_profile', 'sonnet_46', 'Default Claude model profile for chat/runtime policy'),
    ('model_tier_cheap', 'haiku', 'Model for low-cost/low-complexity tasks'),
    ('model_tier_balanced', 'sonnet', 'Model for medium-complexity tasks'),
    ('model_tier_frontier', 'opus', 'Model for high-complexity planning tasks'),
    ('engineer_model', 'sonnet', 'Claude model for Engineer agent'),
    ('father_model', 'sonnet', 'Claude model for Father agent'),
    ('ian_master_model', 'sonnet', 'Claude model for IAn Master agent'),
    ('artisan_master_model', 'sonnet', 'Claude model for Artisan Master agent'),
    ('lavprishjemmeside_master_model', 'sonnet', 'Claude model for Lavprishjemmeside Master agent'),
    ('samlino_master_model', 'sonnet', 'Claude model for Samlino Master agent'),
    ('personal_assistant_master_model', 'sonnet', 'Claude model for Personal Assistant Master agent'),
    ('baltzer_master_model', 'sonnet', 'Claude model for Baltzer Master agent'),
    ('max_task_retries', '3', 'Max retries before escalation'),
    ('claude_timeout_seconds', '120', 'Claude CLI timeout seconds'),
    ('cors_origin', 'http://localhost:8001', 'Allowed CORS origin'),
    ('ENABLE_SPECIALIST_RUNTIME', '0', 'Feature flag for specialist runtime'),
    ('ENABLE_MASTER_DIRECT_EXECUTION', '0', 'Allow masters to execute directly'),
    ('ENABLE_SPECIALIST_TOOL_WRITES', '0', 'Allow specialist write-capable tools'),
    ('ENABLE_APP_GOVERNORS', '1', 'Enable app governors in specialist sync'),
    ('UI_CLAUDE_CONTROL_ENABLED', '0', 'Enable Claude model control cards in workspace UI'),
    ('CHAT_CONTEXT_REFRESH_ENABLED', '0', 'Enable guided context refresh flow in chat workspace'),
    ('CHAT_LIBRARY_PRELOAD_MAX_TOKENS', '80000', 'Maximum estimated tokens allowed for first-turn raw library preload'),
    ('UI_PROJECT_COCKPIT_ENABLED', '1', 'Enable project intelligence cockpit UI and APIs'),
    ('WORKSPACE_UI_MODE', 'atlas_v1', 'Workspace UI mode selector (workspace_v2|atlas_v1)'),
    ('WORKSPACE_DEFAULT_VIEW', 'projects', 'Workspace default top-level view (agents|projects)'),
    ('WORKSPACE_REPORT_DEFAULT_RANGE', 'mtd', 'Default reporting range preset for workspace project dashboards'),
    ('model_profile_opus_46', 'claude-opus-4-6', 'Claude model string for Opus 4.6 profile'),
    ('model_profile_sonnet_46', 'claude-sonnet-4-6', 'Claude model string for Sonnet 4.6 profile'),
    ('model_profile_haiku_45', 'claude-haiku-4-5', 'Claude model string for Haiku 4.5 profile'),
    ('model_profile_haiku_30', 'claude-3-haiku-20240307', 'Claude model string for Haiku 3.0 profile'),
    ('model_profile_haiku_30_enabled', '0', 'Disable Haiku 3.0 legacy profile'),
    ('model_policy_engineer_only_opus', '1', 'Allow Opus profile only for engineer agent'),
    ('ORCH_CONTRACT_MODE', 'warn_only', 'Orchestration contract governance mode'),
    ('ORCH_BOUNDARY_MODE', 'matrix', 'Boundary selection mode for orchestrators'),
    ('ORCH_COMPRESSION_REQUIRED', '1', 'Require map-reduce compression contract'),
    ('ORCH_ESCALATION_WARN_ONLY', '1', 'Warn-only quality checks for escalation packets'),
    ('KANBAN_ENABLED', '0', 'Enable Kanban dashboard routes and UI shell'),
    ('KANBAN_TRANSITIONS_ENABLED', '0', 'Enable guarded Kanban transition write endpoint'),
    ('KANBAN_HYGIENE_AUTO_ARCHIVE', '0', 'Allow Kanban hygiene apply archive mode'),
    ('KANBAN_MANUAL_UI', '0', 'Show manual transition controls in Kanban UI'),
    ('KANBAN_MANUAL_TRANSITIONS_API', '0', 'Allow manual transition writes from Kanban endpoints'),
    ('ENGINEER_CONTEXT_GUARD_REQUIRED', '1', 'Require context links and memory delta before engineer task completion'),
    ('ARTISAN_MASTER_SSH_SCOPE', 'controlled_ops', 'Artisan master SSH authority policy'),
    ('ARTISAN_MASTER_INTAKE_MODE', 'workspace_queue', 'Artisan master intake handling mode'),
    ('ARTISAN_WP_THEME_IDENTITY_ENFORCED', '1', 'Enforce Saren child theme identity for The Artisan'),
    ('AUTONOMY_ENABLED', '0', 'Soft kill switch for all autonomous actions'),
    ('AUTONOMY_MODE', 'dry_run', 'Autonomy mode (off|dry_run|provision)'),
    ('AUTONOMY_REPO_PROVISIONING_ENABLED', '0', 'Allow topology-driven repo provisioning preflight and later live execution'),
    ('AUTONOMY_ALLOWED_REPOSITORY_IDS', '', 'Comma-separated repository ids allowed for autonomous repo provisioning'),
    ('AUTONOMY_REQUIRE_STRICT_VALIDATION', '1', 'Require strict validation before autonomy escalates beyond preflight'),
    ('AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS', '0', 'Allow destructive autonomy actions such as remote deletion'),
    ('AUTONOMY_AUDIT_READY', '0', 'Durable audit plumbing readiness gate for live autonomy writes'),
    ('AUTONOMY_EXECUTOR_ENABLED', '0', 'Allow the always-on autonomy executor to trigger IAn or Engineer runs'),
    ('AUTONOMY_EXECUTOR_ALLOWED_AGENTS', 'ian-master,engineer', 'Comma-separated agent ids allowed to run on the autonomy executor host');

INSERT OR IGNORE INTO master_agents (id, name, type, status, description) VALUES
    ('father', 'IAn', 'orchestrator', 'active', 'Top-level orchestration authority'),
    ('engineer', 'Engineer Agent', 'special', 'idle', 'Builds and fixes the system'),
    ('ian-master', 'IAn Legacy Alias', 'domain', 'idle', 'Legacy compatibility alias for top-level IAn orchestration'),
    ('artisan-master', 'Artisan Master Agent', 'domain', 'idle', 'Owns The Artisan systems, WordPress/B2B, and Brevo operations'),
    ('lavprishjemmeside-master', 'Lavprishjemmeside Master Agent', 'domain', 'idle', 'Owns AI CMS, SEO/Ads dashboards, and client subscriptions'),
    ('samlino-master', 'Samlino Master Agent', 'domain', 'idle', 'Owns Samlino AI and product-management delivery'),
    ('personal-assistant-master', 'Personal Assistant Master Agent', 'domain', 'idle', 'Owns task/calendar/email/social/fitness assistant systems'),
    ('baltzer-master', 'Baltzer Master Agent', 'domain', 'idle', 'Owns Shopify, TCG index, events, workforce, and accounting integration');

INSERT OR IGNORE INTO agent_context_limits (agent_id, context_limit_tokens, warning_threshold, updated_at) VALUES
    ('father', 200000, 0.80, datetime('now')),
    ('engineer', 180000, 0.80, datetime('now')),
    ('masters:ian-master', 120000, 0.80, datetime('now')),
    ('masters:artisan-master', 120000, 0.80, datetime('now')),
    ('masters:lavprishjemmeside-master', 120000, 0.80, datetime('now')),
    ('masters:samlino-master', 120000, 0.80, datetime('now')),
    ('masters:personal-assistant-master', 120000, 0.80, datetime('now')),
    ('masters:baltzer-master', 120000, 0.80, datetime('now'));

INSERT OR IGNORE INTO agent_controls (agent_id, autonomous_sync, require_schema_approval, debug_mode, updated_at) VALUES
    ('father', 1, 1, 0, datetime('now')),
    ('engineer', 1, 1, 0, datetime('now')),
    ('ian-master', 1, 1, 0, datetime('now')),
    ('artisan-master', 1, 1, 0, datetime('now')),
    ('lavprishjemmeside-master', 1, 1, 0, datetime('now')),
    ('samlino-master', 1, 1, 0, datetime('now')),
    ('personal-assistant-master', 1, 1, 0, datetime('now')),
    ('baltzer-master', 1, 1, 0, datetime('now'));

INSERT OR IGNORE INTO program_registry (id, name, domain, owner_master_id, repo_path, stack, app_status, notes) VALUES
    ('ian-control-plane', 'IAn Agency Control Plane', 'platform', 'father', '.', 'python-fastapi-sqlite', 'active', 'Sellable IAn Agency governance layer, mission-control dashboard, and orchestration core'),
    ('artisan-reporting', 'Artisan Reporting', 'artisan', 'artisan-master', 'programs/artisan/reporting.theartisan.dk', 'node-express-ejs', 'active', 'Billy-integrated reporting application'),
    ('artisan-wordpress', 'Artisan WordPress', 'artisan', 'artisan-master', 'programs/artisan/the-artisan-wp', 'wordpress-php-woocommerce', 'active', 'cPanel-hosted WordPress/B2B'),
    ('artisan-email-marketing', 'Artisan Email Marketing', 'artisan', 'artisan-master', 'programs/artisan/e-mail-marketing', 'html-email-brevo', 'planned', 'Brevo campaign conversion workspace'),
    ('lavprishjemmeside-cms', 'Lavprishjemmeside CMS', 'lavprishjemmeside', 'lavprishjemmeside-master', 'ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/lavprishjemmeside.dk', 'astro-node-mysql', 'active', 'Remote-first CMS that governs lavprishjemmeside.dk and ljdesignstudio.dk client sites'),
    ('samlino-seo-agent-playground', 'Samlino Agency Context', 'samlino', 'samlino-master', 'programs/ian-agency/contexts/samlino/seo-agent-playground', 'react-fastapi-controlplane-sqlite', 'active', 'Archive-mapped strategy and sandbox context carried under IAn Agency'),
    ('baltzer-tcg-index', 'Baltzer TCG Index', 'baltzer', 'baltzer-master', 'programs/baltzer/TCG-index', 'react-migration-hold', 'planned', 'Demoted from the live operational surface pending local datastore replacement'),
    ('baltzer-reporting', 'Baltzer Reporting', 'baltzer', 'baltzer-master', 'programs/baltzer/reporting.baltzergames.dk', 'node-express-ejs', 'active', 'Accounting/reporting application'),
    ('baltzer-shopify', 'Baltzer Shopify', 'baltzer', 'baltzer-master', 'programs/baltzer/shopify', 'shopify-ecommerce', 'active', 'Shopify operational workspace'),
    ('personal-assistant-suite', 'Personal Assistant Suite', 'personal-assistant', 'personal-assistant-master', 'programs/personal-assistant', 'multi-tooling', 'planned', 'Task/calendar/social/email/fitness assistant scope');

INSERT OR IGNORE INTO application_registry (
    id, program_id, name, owner_master_id, status, kind, repo_path, frontend_entry, backend_entry, dev_url, notes, created_at, updated_at
) VALUES
    (
        'ian-mission-control',
        'ian-control-plane',
        'IAn Mission Control',
        'father',
        'active',
        'core',
        'backend/static',
        'backend/static/index.html',
        'backend/main.py',
        'http://localhost:8001',
        'Unified control surface for orchestration, agents, and tasks',
        datetime('now'),
        datetime('now')
    );

INSERT OR IGNORE INTO data_store_registry (id, program_id, name, engine, role, location, env_keys, status, notes) VALUES
    ('father-db', 'ian-control-plane', 'father.db', 'sqlite', 'orchestration', 'father.db', 'DB_PATH', 'unknown', 'WAL-enabled orchestration DB'),
    ('artisan-reporting-local-state', 'artisan-reporting', 'Artisan Reporting cPanel MySQL', 'mysql_cpanel', 'app_primary', 'cpanel:mysql', 'ARTISAN_REPORTING_DB_HOST,ARTISAN_REPORTING_DB_PORT,ARTISAN_REPORTING_DB_NAME,ARTISAN_REPORTING_DB_USER,ARTISAN_REPORTING_DB_PASSWORD,BILLY_API_TOKEN', 'unknown', 'Dedicated reporting MySQL database on cPanel plus Billy API token'),
    ('artisan-wordpress-cpanel-mysql', 'artisan-wordpress', 'Artisan WP cPanel MySQL', 'mysql_cpanel', 'app_primary', 'cpanel:mysql', 'ARTISAN_WP_DB_HOST,ARTISAN_WP_DB_USER,ARTISAN_WP_DB_PASSWORD,ARTISAN_WP_DB_NAME', 'unknown', 'WordPress database on cPanel'),
    ('lavprishjemmeside-cpanel-mysql', 'lavprishjemmeside-cms', 'Lavprishjemmeside cPanel MySQL', 'mysql_cpanel', 'app_primary', 'cpanel:mysql', 'DB_HOST,DB_USER,DB_PASSWORD,DB_NAME', 'unknown', 'Primary CMS database on cPanel'),
    ('samlino-module-storage', 'samlino-seo-agent-playground', 'Samlino Local SQLite', 'sqlite', 'app_primary', 'programs/ian-agency/contexts/samlino/seo-agent-playground/data/samlino.db', '', 'unknown', 'Program-local SQLite datastore for Samlino modules'),
    ('baltzer-tcg-migration-hold', 'baltzer-tcg-index', 'Baltzer TCG Migration Hold', 'planned', 'app_primary', 'programs/baltzer/TCG-index/MIGRATION-HOLD.md', '', 'planned', 'Legacy hosted datastore removed from the live surface; local replacement pending'),
    ('baltzer-reporting-local-state', 'baltzer-reporting', 'Baltzer Reporting Local State', 'json_file', 'app_primary', 'programs/baltzer/reporting.baltzergames.dk/data', 'BILLY_API_TOKEN', 'unknown', 'JSON files and Billy API token'),
    ('baltzer-shopify-cloud', 'baltzer-shopify', 'Baltzer Shopify', 'shopify_cloud', 'app_primary', 'shopify:cloud', 'SHOPIFY_STORE_DOMAIN,SHOPIFY_ADMIN_TOKEN', 'unknown', 'Shopify managed platform'),
    ('personal-assistant-local', 'personal-assistant-suite', 'Personal Assistant Local', 'planned', 'app_primary', 'programs/personal-assistant', '', 'planned', 'Pending data-store implementation');

INSERT OR IGNORE INTO agent_program_assignments (id, agent_id, program_id, responsibility, priority, status, notes) VALUES
    ('engineer:ian-control-plane', 'engineer', 'ian-control-plane', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:artisan-reporting', 'engineer', 'artisan-reporting', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:artisan-wordpress', 'engineer', 'artisan-wordpress', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:artisan-email-marketing', 'engineer', 'artisan-email-marketing', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:lavprishjemmeside-cms', 'engineer', 'lavprishjemmeside-cms', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:samlino-seo-agent-playground', 'engineer', 'samlino-seo-agent-playground', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:baltzer-tcg-index', 'engineer', 'baltzer-tcg-index', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:baltzer-reporting', 'engineer', 'baltzer-reporting', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:baltzer-shopify', 'engineer', 'baltzer-shopify', 'owner', 'P1', 'active', 'Engineering authority'),
    ('engineer:personal-assistant-suite', 'engineer', 'personal-assistant-suite', 'owner', 'P1', 'active', 'Engineering authority'),
    ('father:ian-control-plane', 'father', 'ian-control-plane', 'owner', 'P1', 'active', 'Domain ownership'),
    ('artisan-master:artisan-reporting', 'artisan-master', 'artisan-reporting', 'owner', 'P1', 'active', 'Domain ownership'),
    ('artisan-master:artisan-wordpress', 'artisan-master', 'artisan-wordpress', 'owner', 'P1', 'active', 'Domain ownership'),
    ('artisan-master:artisan-email-marketing', 'artisan-master', 'artisan-email-marketing', 'owner', 'P1', 'active', 'Domain ownership'),
    ('lavprishjemmeside-master:lavprishjemmeside-cms', 'lavprishjemmeside-master', 'lavprishjemmeside-cms', 'owner', 'P1', 'active', 'Domain ownership'),
    ('samlino-master:samlino-seo-agent-playground', 'samlino-master', 'samlino-seo-agent-playground', 'owner', 'P1', 'active', 'Domain ownership'),
    ('baltzer-master:baltzer-tcg-index', 'baltzer-master', 'baltzer-tcg-index', 'owner', 'P1', 'active', 'Domain ownership'),
    ('baltzer-master:baltzer-reporting', 'baltzer-master', 'baltzer-reporting', 'owner', 'P1', 'active', 'Domain ownership'),
    ('baltzer-master:baltzer-shopify', 'baltzer-master', 'baltzer-shopify', 'owner', 'P1', 'active', 'Domain ownership'),
    ('personal-assistant-master:personal-assistant-suite', 'personal-assistant-master', 'personal-assistant-suite', 'owner', 'P1', 'active', 'Domain ownership');
