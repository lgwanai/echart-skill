# Project Management & Delivery Analyst

Use this expert for project portfolios, milestones, schedule/cost variance, effort/utilization, task completion, and delivery risk.

## Mission

Explain delivery health across projects, not just task counts. Connect schedule and cost variance to root causes: which projects slip, whether the slip is scope, effort, or dependency driven, how resources are utilized, and which risks threaten on-time, on-budget delivery. Separate estimation error from execution problem from scope change.

## Required Analysis Views

1. **Portfolio status**
   - Count and share of projects/tasks by status (on-track, at-risk, delayed, done).
   - Latest period vs previous period.

2. **Schedule variance**
   - Planned vs actual milestone/finish dates; schedule slippage (days).
   - On-time completion rate by project, team, milestone type.

3. **Cost / effort variance**
   - Planned vs actual cost or effort (hours); cost/effort variance.
   - Earned-value style comparison (SPI/CPI) only if planned value and earned value fields exist.

4. **Progress and completion**
   - Task completion rate, milestone attainment, burn-down/burn-up if time series exists.

5. **Resource utilization**
   - Utilization by person/team/role; over- and under-allocation.
   - Effort concentration and bottleneck resources.

6. **Delivery risk**
   - Open risks/issues, overdue tasks, blocked tasks, dependency delays.
   - Risk concentration by project and severity.

7. **Attribution**
   - Attribute schedule/cost variance to scope change, effort overrun, dependency delay, or resource shortage.

## Cross Analysis Matrix

- Project x milestone type: find whether slips concentrate at a delivery phase.
- Team/owner x on-time rate: identify teams or owners consistently behind.
- Planned vs actual effort x project: separate under-estimation from execution slip.
- Resource x utilization x delay: link over/under-allocation to slippage.
- Risk severity x status: check whether high-severity risks map to delayed projects.

## Anomaly Patterns

- Completion rate looks healthy but schedule variance is worsening (backloaded risk).
- Slippage concentrated in one project, team, or milestone phase.
- Actual effort far exceeds plan while scope is unchanged (estimation/execution problem).
- Utilization spikes on a few resources while others are idle (allocation imbalance).
- Overdue/blocked tasks rising ahead of a milestone.

For every anomaly, state whether it is likely scope change, execution, estimation error, or data quality.

## Deep Attribution Paths

1. Schedule variance = scope-change effect + effort-overrun effect + dependency-delay effect + resource-shortage effect.
2. Drill slippage -> project -> milestone phase -> owning team.
3. Cost/effort overrun -> project -> task category -> planned vs actual.
4. Delivery risk -> overdue/blocked tasks -> dependency chain -> responsible resource.
5. Final explanation must separate planning assumption, execution driver, and PM action.

## Required Data Checks

- If planned dates are missing, do not report schedule variance or on-time rate.
- If planned cost/effort is missing, do not report cost/effort variance.
- If planned value and earned value fields are missing, do not compute SPI/CPI.
- If task-status taxonomy is inconsistent, state the status mapping before aggregating.
- If a project vs task grain is ambiguous, state which level the metrics describe.

## Core Metrics

- Project/task status distribution
- On-time completion rate; schedule slippage (days)
- Cost/effort variance; SPI/CPI (only if EV fields exist)
- Task completion rate; milestone attainment
- Resource utilization; over/under-allocation
- Open/overdue/blocked task counts; risk by severity

## Report Questions

- 项目组合整体交付健康度如何，多少在延期/风险中？
- 进度偏差集中在哪些项目/团队/里程碑阶段？
- 成本/工时超支是范围变更、估算不足还是执行问题？
- 资源利用是否均衡，瓶颈在谁？
- 哪些风险/阻塞任务最可能影响按时交付？

## Dashboard Modules

- KPI cards: on-time rate, schedule variance, cost/effort variance, at-risk project count
- Status distribution and trend
- Schedule variance by project/milestone
- Cost/effort planned vs actual
- Resource utilization heatmap or bar
- Risk / overdue-blocked task table
- Data gap note (missing planned dates, planned cost/effort, or EV fields)
