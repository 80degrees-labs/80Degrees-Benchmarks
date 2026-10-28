"""Build two reports and data-derived charts from the public analysis artifacts."""
import json
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'public/studies/october-2026'
CHARTS=DATA/'charts'
TEMP=ROOT/'tmp/pdfs'
PDF=ROOT/'output/pdf'
A=json.loads((DATA/'analysis.json').read_text())
C=json.loads((DATA/'api-equivalent-costs.json').read_text())
P=json.loads((DATA/'provenance.json').read_text())
ROWS=json.loads((DATA/'task-results.json').read_text())
MODELS=['gpt-6.1-sol','gpt-6-astra']
NAMES=['6.1 Sol','6 Astra']
TEAL='#087f8c'; BLUE='#4056a1'; GREY='#cbd5e1'; AMBER='#c57b17'; INK='#17243a'
for d in [CHARTS,TEMP,PDF,DATA/'reports']: d.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'svg.fonttype':'none','figure.facecolor':'white'})


def savefig(name,fig):
    fig.savefig(CHARTS/(name+'.svg'),bbox_inches='tight',metadata={'Date':'2026-10-28'})
    svg = CHARTS/(name+'.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(TEMP/(name+'.png'),dpi=170,bbox_inches='tight')
    plt.close(fig)


def charts():
    fig,ax=plt.subplots(figsize=(8,3.5))
    x=np.arange(2); w=.32
    for j,(key,label,color) in enumerate([('native_solved','80 Degrees',TEAL),('codex_solved','Codex CLI',BLUE)]):
        vals=[100*A['models'][m]['raw'][key]/A['models'][m]['raw']['n'] for m in MODELS]
        bars=ax.bar(x+(j-.5)*w,vals,w,label=label,color=color)
        ax.bar_label(bars,labels=[f"{A['models'][m]['raw'][key]}/{A['models'][m]['raw']['n']} ({v:.1f}%)" for m,v in zip(MODELS,vals)],padding=4,fontsize=10)
    ax.set_xticks(x,NAMES); ax.set_ylim(0,100); ax.set_ylabel('Raw verifier success (%)'); ax.legend(loc='upper right',frameon=False)
    ax.set_title('Observed correctness - raw scores, medium reasoning',loc='left',weight='bold',pad=14)
    fig.text(.12,-.03,'Raw zeroes include verifier failures; see the evidence-quality analysis.',fontsize=9,color='#536176')
    savefig('correctness',fig)

    fig,axs=plt.subplots(1,2,figsize=(8,3.8))
    for ax,m,n in zip(axs,MODELS,NAMES):
        r=A['models'][m]['raw']; values=[r['both_solved'],r['native_only'],r['codex_only'],r['both_failed']]
        ax.pie(values,colors=[GREY,TEAL,BLUE,AMBER],autopct=lambda p:f'{p:.0f}%' if p>0 else '',startangle=90,wedgeprops={'width':.46,'edgecolor':'white'},pctdistance=.78)
        ax.text(0,0,f"{r['n']}\npairs",ha='center',va='center',weight='bold',fontsize=13)
        ax.set_title(n,weight='bold')
    fig.legend(['Both solve','80 Degrees only','Codex only','Neither solves'],loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,-.03))
    fig.suptitle('Paired raw outcomes - descriptive, not adjudicated pass rates',fontsize=12,weight='bold')
    savefig('paired-outcomes',fig)

    fig,ax=plt.subplots(figsize=(8,3.7)); keys=['tokens_raw_complete','tokens_resolved_complete','tokens_both_solved_descriptive']
    for j,(m,n,c) in enumerate(zip(MODELS,NAMES,[TEAL,BLUE])):
        vals=[A['models'][m][k]['ratio'] for k in keys]; bars=ax.bar(np.arange(3)+(j-.5)*.34,vals,.34,color=c,label=n)
        ax.bar_label(bars,labels=[f'{v:.2f}x\nn={A["models"][m][k]["n"]}' for v,k in zip(vals,keys)],padding=3,fontsize=9,bbox={'facecolor':'white','edgecolor':'none','pad':1})
    ax.axhline(1,color=INK,lw=1,linestyle='--'); ax.set_ylim(0,1.6)
    ax.set_xticks(range(3),['Raw complete pairs','Resolved complete pairs','Both solved (selected)']); ax.set_ylabel('80 Degrees / Codex total tokens'); ax.legend(frameon=False)
    ax.set_title('Token ratios depend on which outcomes are compared',loc='left',weight='bold',pad=12)
    fig.text(.12,-.035,'Below 1 = fewer tokens. Complete telemetry only; subsets are descriptive.',fontsize=9,color='#536176')
    savefig('token-ratios',fig)

    fig,ax=plt.subplots(figsize=(8,3.6))
    vals=[248,58,42,4,4]; labels=['Verified passes: 248','Verified failures: 58','Verifier unavailable: 42','Mixed browser failures: 4','Historical exclusions: 4']
    wedges,_,_=ax.pie(vals,colors=[TEAL,BLUE,AMBER,'#8975a4',GREY],startangle=90,autopct=lambda p:f'{p:.1f}%' if p>2 else '',wedgeprops={'edgecolor':'white'})
    ax.legend(wedges,labels,loc='center left',bbox_to_anchor=(1,.5),frameon=False)
    ax.set_title('Evidence quality across all 356 cells',weight='bold'); savefig('evidence-quality',fig)

    fig,axs=plt.subplots(1,2,figsize=(8,3.5))
    for ax,m,n in zip(axs,MODELS,NAMES):
        keys=['raw_complete','both_solved']
        for j,(key,label,color) in enumerate([('native_usd','80 Degrees',TEAL),('codex_usd','Codex CLI',BLUE)]):
            vals=[C['models'][m][k][key] for k in keys]
            bars=ax.bar(np.arange(2)+(j-.5)*.34,vals,.34,label=label,color=color)
            ax.bar_label(bars,labels=[f'${x:.2f}' for x in vals],padding=3,fontsize=9)
        ax.set_xticks([0,1],['Raw complete','Both solved']); ax.set_title(n,weight='bold'); ax.set_ylim(0,max(C['models'][m]['raw_complete']['codex_usd'],C['models'][m]['raw_complete']['native_usd'])*1.3)
        ax.set_ylabel('API-equivalent USD')
    axs[0].legend(frameon=False,fontsize=8)
    fig.subplots_adjust(top=.80,wspace=.35)
    fig.suptitle('Standard API-equivalent cost - observed cache mix',fontsize=12,weight='bold')
    fig.text(.12,-.025,'Estimated text-token cost, not subscription charges. Subsets have different coverage.',fontsize=9)
    savefig('api-equivalent-cost',fig)


STYLES=getSampleStyleSheet()
STYLES.add(ParagraphStyle(name='Title80',fontName='Helvetica-Bold',fontSize=27,leading=31,textColor=colors.HexColor(INK),spaceAfter=16))
STYLES.add(ParagraphStyle(name='H80',fontName='Helvetica-Bold',fontSize=16,leading=20,textColor=colors.HexColor(INK),spaceAfter=10))
STYLES.add(ParagraphStyle(name='Body80',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=9,textColor=colors.HexColor(INK)))
STYLES.add(ParagraphStyle(name='Small80',fontName='Helvetica',fontSize=8.3,leading=11,spaceAfter=7,textColor=colors.HexColor('#536176')))
STYLES.add(ParagraphStyle(name='Cell80',fontName='Helvetica',fontSize=8.7,leading=11,textColor=colors.HexColor(INK)))


def para(t,style='Body80'):
    return Paragraph(t,STYLES[style])


def table(rows,widths):
    data=[[para(escape(str(c)),'Cell80') for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef4')),
                          ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
                          ('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#94a3b8')),
                          ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8fa')])]))
    return t


def pic(name,width=510):
    from PIL import Image as PILImage
    path=TEMP/(name+'.png'); w,h=PILImage.open(path).size
    return Image(str(path),width=width,height=width*h/w)


def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#dbe2ea')); canvas.line(42,39,570,39)
    canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#536176'))
    canvas.drawString(42,26,'80 DEGREES  /  TERMINAL-BENCH 2.0  /  28 OCT 2026')
    canvas.drawRightString(570,26,str(doc.page))


def build(name,story,title):
    path=PDF/name
    doc=SimpleDocTemplate(str(path),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=53,
                          title=title,author='80 Degrees',subject='Final assessment of available benchmark evidence')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    shutil.copy2(path,DATA/'reports'/name)


def investor():
    story=[para('80 Degrees<br/>Benchmark evidence','Title80'),
           para('Investor assessment | Final conclusions on available evidence | 28 October 2026','Small80'),
           para('<b>Observed scorecard: Sol is a draw; Astra favors Codex on task success.</b> 80 Degrees uses fewer total tokens and has lower Standard API-equivalent cost on complete raw pairs. These are completed measurements, not a cancelled study. Equal-correctness efficiency is a separate test that this study does not pass.'),
           table([['Question','Observed result and claim decision'],['A: More tasks solved','Sol: draw (62 vs 62). Astra: Codex ahead (65 vs 59). No 80 Degrees superiority claim.'],
                  ['B: Comparable correctness, fewer tokens','80 Degrees uses 23.8% / 27.5% fewer raw complete-pair tokens. The comparable-correctness requirement is not met.'],
                  ['B: Lower API-equivalent token cost','80 Degrees estimates are 1.6% / 12.1% lower on raw complete pairs. This is modeled cost, not subscription spending.']],[180,348]),Spacer(1,10),pic('correctness'),
           para('Scope: 89 Terminal-Bench 2.0 tasks per model, medium reasoning, 80 Degrees native headless single-agent profile versus Codex CLI 0.163.0. 352 scored cells; four historical exclusions. This is first-party research, not independent certification.','Small80'),PageBreak(),
           para('Correctness and uncertainty','Title80'),
           para('The paired comparison is the unit of analysis. Equal observed success is not evidence of equivalence. Negative point estimates are also not, by themselves, proof of inferiority.'),
           table([['Raw metric','6.1 Sol','6 Astra'],['Paired tasks','87','89'],['80 Degrees / Codex successes','62 / 62','59 / 65'],['Success difference (80D - Codex)','0.0 percentage points','-6.7 percentage points'],['80D-only / Codex-only solves','6 / 6','6 / 12'],['Exact McNemar p','1.0000','0.2379'],['Holm-adjusted p (two models)','1.0000','0.4758'],['Conservative 95% one-sided lower difference bound','-11.84 percentage points','-19.85 percentage points'],['Noninferiority requirement','Lower bound > -5 points','Lower bound > -5 points'],['Noninferiority established?','No','No']],[256,136,136]),Spacer(1,12),
           para('Evidence-quality sensitivity','H80'),
           para('Excluding pairs with an unavailable verifier leaves 74 Sol pairs (60 vs 61 successes) and 75 Astra pairs (58 vs 60). Their lower difference bounds remain below the -5-point margin: -13.58 and -16.09 points. Exclusion is a sensitivity analysis, not a replacement headline.'),
           para('Across all 89 task slots, allowing unresolved outcomes and historical exclusions to take either value yields observed-difference ranges of <b>-14.61 to +14.61 points</b> for Sol and <b>-15.73 to +6.74 points</b> for Astra. These are missing-outcome bounds, not confidence intervals. Expanding unknowns to the mixed browser failures widens them further.'),
           para('Decision: neither the predeclared statistical gate nor robustness to unresolved outcomes supports Claim A or the correctness component of Claim B.'),PageBreak(),
           para('Tokens: a qualified signal','Title80'),pic('token-ratios'),
           table([['Complete raw pairs','6.1 Sol (86 pairs)','6 Astra (88 pairs)'],['80 Degrees input + output','29,679,726','25,281,642'],['Codex input + output','38,966,944','34,886,113'],['Observed reduction','23.8%','27.5%'],['Paired bootstrap central 95% ratio interval','0.563 to 1.047','0.488 to 1.035'],['One-sided 95% upper ratio bound','0.995','0.984']],[240,144,144]),Spacer(1,10),
           para('The correctness gate fails before token savings can substantiate Claim B. Even the two-sided token intervals include a ratio of 1. Both-solved subsets show 20.9% fewer tokens for Sol but <b>21.6% more for Astra</b>. These outcome-selected subsets are descriptive, not causal or equivalent-correctness tests.'),
           para('Two native timeout trials have missing usage; complete pairs omit the matched Codex trials too. Cached tokens are included in input once; reasoning is included in output. No missing measurement is replaced with zero. Early unfinished exits can reduce tokens while reducing usefulness.'),
           para('Cost: Standard API-equivalent estimates are now calculated from official rates and the observed cache mix; see the cost appendix. They favor 80 Degrees on raw complete pairs but favor Codex on both-solved pairs. They are not observed subscription charges.'),PageBreak(),
           para('What the evidence can support','Title80'),pic('evidence-quality'),
           para('42 raw zeroes have an unavailable verifier: 31 Python-download timeouts, nine network/package setup failures and two interrupted package-manager states. Four additional zeroes mix output assertions with browser dependency errors and remain failures in the primary raw view. The precise cause of every environment failure is not attributed to the provider or harness.'),
           table([['Recorded ledger disposition','Count'],['Scored cells','352'],['Historical reservations (four excluded cells)','10'],['Explicit provider-capacity failures','7'],['Local missing-runtime failure before model launch','1'],['Total recorded reservations','370']],[410,118]),Spacer(1,10),
           para('<b>Defensible investor wording:</b> "In a first-party, medium-reasoning Terminal-Bench 2.0 study, 80 Degrees matched Codex\'s raw Sol success count and had lower raw Astra success. On pairs with complete telemetry it used 23.8% and 27.5% fewer tokens, respectively. The study did not establish superior correctness, correctness noninferiority, or actual-dollar savings."'),
           para('Do not shorten this to "same accuracy for less" or "outperforms Codex." Final analysis is complete for the available evidence; unresolved outcomes remain unresolved. No selective paid reruns were added to improve the result.'),PageBreak(),
           para('Reproducibility and limits','Title80'),
           table([['Component','Measured version / revision'],['80 Degrees source base',P['source_base_commit']],['Measured Harbor adapter',P['adapter_commit']],['Native engine checkout',P['engine_commit']],['Codex CLI','0.163.0'],['Harbor','0.24.0 / '+P['harbor_commit']],['Terminal-Bench 2.0',P['dataset_commit']]], [166,362]),Spacer(1,12),
           para('Native profile uses createAgentSession with read, bash, edit, write, grep and todo; no model fallback, delegation or automatic agent retry. Both arms use explicit medium reasoning and fresh sessions. The profile is not the full desktop experience. Apple Silicon host, linux/amd64 emulation; no claim about all hardware or agent versions.'),
           para('Tasks were shuffled with seed 10262026, Sol ran before Astra and arm order alternated. The shared subscription and run order can affect capacity. Maximum three total launch reservations per cell included historical attempts. Scored failures were not retried as best-of-three; these are not pass@3 results. Four previous synthetic integration checks are outside the 370-reservation ledger.'),
           para('Exact paired McNemar with Holm adjustment across models; conservative paired win/loss bounds at alpha .025 per tail; predeclared 5-point noninferiority margin. Token ratios use 50,000 paired percentile-bootstrap samples, seed 10262026. Resampling characterizes task variation; it cannot remove bias from missing results, selected tasks or shared conditions.'),
           para('The protocol followed earlier pilot observations, so it is not pristine preregistration. The parent source tree had a frontend lockfile modification outside the headless build; the actual engine checkout is recorded separately from the parent gitlink. Later portable-adapter commits were not used in this measurement.'),
           para('Public evidence: github.com/80degrees-labs/80Degrees-Benchmarks, public/studies/october-2026. Includes task CSV/JSON, attempt accounting, classifications, hashes, analysis code, charts and both reports. Raw traces remain private; a reviewer must inspect authorized redacted artifacts to independently verify their contents. Hashes alone do not establish correctness. No SWE-bench or competitor-CLI conclusions are made.','Small80')]
    story.extend(cost_page())
    build('80degrees-investor-benchmark-report.pdf',story,'80 Degrees - Investor benchmark assessment')


def refinement():
    groups={}
    for row in ROWS: groups.setdefault((row['model'],row['task']),{})[row['harness']]=row
    regression=[]
    for (m,t),v in groups.items():
        a,b=v['80degrees'],v['codex']
        if a['raw_reward']==b['raw_reward']==1 and all(x['input_tokens'] is not None and x['output_tokens'] is not None for x in (a,b)):
            at=a['input_tokens']+a['output_tokens']; bt=b['input_tokens']+b['output_tokens']
            regression.append((at-bt,m,t,at,bt))
    regression.sort(reverse=True)
    story=[para('80 Degrees<br/>Harness refinement','Title80'),
           para('Engineering evidence and next experiments | 28 October 2026','Small80'),
           para('<b>Observed result: Sol draws; Astra favors Codex on raw correctness.</b> 80 Degrees uses fewer raw complete-pair tokens, with Standard API-equivalent cost estimates 1.6% / 12.1% lower. The comparable-correctness gate is not met. On both-solved pairs, modeled costs favor Codex. Fix completion reliability before claiming equal-quality efficiency.'),
           pic('paired-outcomes'),
           para('Raw paired gaps: Sol has six wins and six losses; Astra six wins and 12 losses. Some discordances are verifier failures, so they are not all harness mistakes. Native wins that have valid paired verification must remain regression cases while fixing weaknesses.'),
           para('Priority order: (1) reconcile verifier availability and improve evidence collection; (2) prevent completion while required work is unfinished; (3) handle task ambiguity and output contracts; (4) investigate token regressions on solved tasks; (5) validate changes on an independent holdout.'),
           para('These tasks become development data once their traces guide tuning. Do not claim a rerun on them is untouched validation. No harness code or frozen agent prompts were changed for this analysis.'),PageBreak(),
           para('Observed failures, bounded hypotheses','Title80'),
           table([['Evidence','Hypothesis and experiment'],
                  ['Sol: compile-compcert; both models: rstan-to-pystan. Final text reports builds or sampling still running; required artifacts absent.', 'Completion gate may not wait for required background work. Track process IDs and exit status; require artifact checks before finalization. Test cancellation and bounded waiting on fresh long-build tasks.'],
                  ['Astra: crack-7z-hash and mcmc-sampling-stan. Final text explicitly says password recovery or RStan installation is unfinished.', 'Separate command launch from completion. Measure unfinished-final rate, artifact validity and elapsed budget. Do not merely extend one arm\'s time limit.'],
                  ['Both models: protein-assembly asks to resolve FASTA placeholders and creates no deliverable.', 'Study noninteractive ambiguity handling. Distinguish defensible assumptions from contradictions needing clarification. Do not suppress legitimate safety or authorization boundaries.'],
                  ['Astra: pytorch-model-recovery saves a model, but verifier reports a forward-call interface error.', 'Validate the user-facing invocation contract, not only local loss/weight checks. Add fresh API-signature and serialization regression tasks.'],
                  ['Astra: sanitize-git-repo fails expected replacement check; uses 1.38M vs 0.26M tokens.', 'Inspect replacement scope and repeated verification. Instrument redundant searches and output-size growth before choosing an optimization.'],
                  ['Sol: mteb-leaderboard; Astra: mteb-retrieve produce the wrong expected answer.', 'Audit date, source, ranking and exact task contract. Do not hardcode verifier answers or assume causal failure from one trace.']],[240,288]),Spacer(1,10),
           para('Astra compile-compcert, build-pov-ray, fix-ocaml-gc and write-compressor have Python-download failures in verification. They must not be counted as confirmed harness-specific correctness defects. The failure taxonomy and individual hashes are in task-results.csv.'),PageBreak(),
           para('Efficiency needs outcome context','Title80'),pic('token-ratios'),
           para('The Astra both-solved set contains 53 tasks: native 16,125,794 tokens versus Codex 13,265,337 (+21.6%). Sol\'s 56 both-solved tasks use 12,969,990 versus 16,394,885 (-20.9%). Neither selected subset establishes overall noninferiority or a causal efficiency advantage.'),
           para('Largest native token excesses on tasks both solve','H80'),
           table([['Model / task','80D tokens','Codex tokens','Excess']]+[[('Sol' if m=='gpt-6.1-sol' else 'Astra')+' / '+t,f'{at:,}',f'{bt:,}',f'{delta:+,}'] for delta,m,t,at,bt in regression[:6]],[258,90,90,90]),Spacer(1,10),
           para('Investigate tool-call repetition, context growth, rejected edits and repeated full-file reads in these traces. These are hypotheses to measure, not established causes. Token budgets should be assessed jointly with correctness; shorter unfinished runs are not successful efficiency improvements.','Small80'),PageBreak(),
           para('Telemetry and runner priorities','Title80'),
           table([['Priority','Change to test','Acceptance criterion'],
                  ['P0: verifier health','Prebuild/pin verifier dependencies; no live Python/package download during scoring. Keep task logic unchanged and record image digests.', 'Synthetic canary verifies runner availability before paid trials; setup failures cannot be silently recorded as solution failures. New protocol for changed environment.'],
                  ['P0: timeout usage','Flush native per-turn usage before timeout termination; retain provider usage provenance and partial/full status.', 'Two make-doom-for-mips native trials currently lack totals. Future forced-timeout tests preserve observed usage without calling partial usage complete.'],
                  ['P0: completion lifecycle','Track pending required processes and declared artifacts at finalization.', 'No final success while a required job is pending; correctly handles failed, canceled and long-running processes within the same budget.'],
                  ['P1: resource handling','Preflight disk and Docker health; cache eviction only for completed tasks. Preserve runtime separately from cleanup targets.', 'Resume skips scored cells; failure evidence and cap remain intact. Runtime removal never triggers repeated paid launch.'],
                  ['P1: comparable identity','Capture actual model, effort and service tier in each provider event, with fail-closed mismatches.', 'No inferred identity from requested flags alone; no fallback or unrecorded mixed model.'],
                  ['P1: efficiency instrumentation','Record per-turn token growth, tool name, duration and output size, with redaction.', 'Explain token regressions on held-out successes without reducing correctness or leaking credentials.']],[90,245,193]),Spacer(1,12),
           para('Provider attribution: seven failures have explicit capacity messages. One reservation failed locally before Harbor could launch. Verifier-network and package-manager failures are a separate category. Do not relabel all errors as provider failures.'),
           para('370 ledger reservations contain 356 attempts with complete reported usage and 14 without complete usage (including the known zero-call local failure). Observed subtotals are lower bounds, not full-study cost comparisons. Synthetic preflights are outside this ledger.'),PageBreak(),
           para('A testable improvement plan','Title80'),
           table([['Step','Design and decision rule'],
                  ['1. Freeze evidence','Retain raw outcomes, failure logs and hashes. Use the public task table to reproduce every aggregate. Keep audit data out of agent prompts.'],
                  ['2. Isolate changes','Use a new commit and one intervention per ablation: lifecycle gate, contract validation, telemetry flush, then context efficiency. Preserve current successes as regressions.'],
                  ['3. New validation set','Use independent tasks with similar long-build, output-contract and ambiguity patterns. Randomize/interleave arms; fix models, efforts, tools, limits and environment before outcomes.'],
                  ['4. Declare evidence requirements','Choose sample size with prospective power analysis and an explicit noninferiority margin. Publish correctness first, then tokens on the identical eligible set. Do not relax the margin after seeing results.'],
                  ['5. Separate reliability from scoring','Keep a capped error ledger. Reverify a saved immutable solution only when the original environment/output is recoverable; do not substitute a new agent attempt for the old outcome.'],
                  ['6. Promote claims only on evidence','Require the full statistical gates and missingness sensitivity. Use actual billing for a money claim. Publish unfavorable results as well as wins.']],[125,403]),Spacer(1,14),
           para('Why no more paid runs were added','H80'),
           para('Existing data are sufficient to decide that the proposed claims are not established. Many containers were deleted after trials, so a fresh agent run would not be verification of the original solution. Historical cells include exhausted attempt caps. Selective reruns after seeing outcomes would bias the headline. A new predeclared validation study is the appropriate next step.'),
           para('Trace provenance','H80'),
           para('Case studies are based on native final message events, paired raw results and verifier logs. Public rows include result/verifier SHA-256 hashes; private paired-evidence.json maps them to retained source files. Facts, hypotheses and proposed experiments are deliberately separate. No new competitor claims or SWE-bench results are implied.'),
           para('Measured source base: '+P['source_base_commit']+'<br/>Measured adapter: '+P['adapter_commit']+'<br/>Engine: '+P['engine_commit']+'<br/>Codex CLI 0.163.0; Harbor 0.24.0. Full provenance and statistical methods accompany the investor report.','Small80')]
    story.extend(cost_page())
    build('80degrees-harness-refinement-report.pdf',story,'80 Degrees - Harness refinement evidence')


def cost_page():
    return [PageBreak(),para('API-equivalent cost scorecard','Title80'),
            para('Official prices checked 28 October 2026. Standard text-token rates applied equally to both harnesses; no regional or priority premium. This answers a modeled-cost question, not actual subscription spending.'),pic('api-equivalent-cost',440),
            table([['Measured subset','Sol: 80D / Codex','Astra: 80D / Codex'],
                   ['Raw complete pairs (86 / 88)','$11.23 / $11.42','$55.99 / $63.68'],
                   ['Observed cost reduction','1.6% lower','12.1% lower'],
                   ['Resolved complete pairs (73 / 74)','$8.34 / $8.82','$45.93 / $44.91'],
                   ['Both-solved pairs (56 / 53)','$5.67 / $5.45','$33.50 / $28.06'],
                   ['Both-solved cost difference','80D 3.9% higher','80D 19.4% higher']],[248,140,140]),Spacer(1,9),
            para('Formula: (uncached input x input rate + cache reads x cached rate + output x output rate) / 1,000,000. Zero cache writes were recorded. Rates per million: Sol $2 / $0.10 / $10; Astra $10 / $1 / $50, respectively. Reasoning and cached input are counted once.'),
            para('No observed request exceeded the 272K-input long-context threshold. Two native aggregate/event residuals are below that threshold and priced from aggregate totals. Missing usage, retries, historical reservations, tool charges and subscription fees are excluded. Rate normalization does not prove what an actual API replay would cost.','Small80'),
            para('Raw paired bootstrap 95% cost-ratio intervals: Sol [0.834, 1.159], Astra [0.689, 1.105]. Both include 1. A lower observed modeled total is a descriptive result, not proven equal-correctness cost superiority. Both-solved subsets are selected by outcomes.','Small80'),
            para('Sources: developers.openai.com/api/docs/pricing; developers.openai.com/api/docs/models/gpt-6.1-sol; developers.openai.com/api/docs/models/gpt-6-astra. Reproduce with tooling/price_usage.py; numeric source-trace audit is in pricing-audit.json.','Small80')]


if __name__=='__main__':
    charts(); investor(); refinement()
    print('Generated two PDFs and five reproducible charts.')
