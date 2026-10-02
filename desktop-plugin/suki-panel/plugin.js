import { host, useValue, Button, PANES_AREA, PALETTE_AREA } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'

const PLUGIN_ID = 'suki-panel'

const ACTIONS = [
  {
    label: 'Find customers needing recovery',
    hint: 'Runs PromiseGuard triage for Cubao.',
    prompt:
      'Use the suki-promiseguard-recovery skill. Call mcp_suki_find_recovery_cases for branch Cubao limit 10, then present the top 3 cases and why they rank highest.'
  },
  {
    label: 'Open evidence-backed case card',
    hint: 'Prepares a PromiseGuard evidence card for TCK-0007.',
    prompt:
      'Use the suki-promiseguard-recovery skill. Call mcp_suki_publish_recovery_card for ticket_id TCK-0007 and render the card sections: customer experience, operations, evidence, recovery plan, promise check.'
  },
  {
    label: 'Approve & assign (demo case)',
    hint: 'Applies recovery action and verifies read-back state.',
    prompt:
      'Use the suki-promiseguard-recovery skill. Prepare plan for TCK-0007, then apply approved action with the returned plan token and owner. Read back with mcp_suki_get_recovery_result and show before/after owner+status, action ID, and the notes Draft only—not sent / Assigned—not resolved.'
  }
]

async function send(prompt) {
  const ok = host.composer.submit(null, prompt)
  if (!ok) host.notify({ kind: 'info', message: 'Open or focus a chat first, then click again.' })
}

function ActionRow({ action, disabled }) {
  return jsxs('div', {
    className: 'flex flex-col gap-1 rounded-md border border-(--ui-stroke-secondary) p-2',
    children: [
      jsx(Button, {
        disabled,
        onClick: () => send(action.prompt),
        children: action.label
      }),
      jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: action.hint })
    ]
  })
}

function SukiPanel() {
  const busy = useValue(host.state.busy)
  return jsxs('div', {
    className: 'flex h-full flex-col gap-3 overflow-auto p-3 text-sm',
    children: [
      jsxs('div', {
        children: [
          jsx('div', { className: 'font-medium', children: 'Suki PromiseGuard' }),
          jsx('div', {
            className: 'text-xs text-(--ui-text-tertiary)',
            children: busy ? 'Hermes is working…' : 'GUI → Skill → MCP → verified result.'
          })
        ]
      }),
      ...ACTIONS.map((a) => jsx(ActionRow, { action: a, disabled: busy }, a.label))
    ]
  })
}

export default {
  id: PLUGIN_ID,
  name: 'Suki PromiseGuard',
  register(ctx) {
    ctx.register({
      id: 'pane',
      area: PANES_AREA,
      title: 'PromiseGuard',
      data: { placement: 'right', width: '320px' },
      render: () => jsx(SukiPanel, {})
    })
    ctx.register({
      id: 'run-first',
      area: PALETTE_AREA,
      data: {
        id: `${PLUGIN_ID}.run`,
        label: `Suki: ${ACTIONS[0].label}`,
        keywords: ['suki', 'promiseguard', 'camp', 'run'],
        run: () => send(ACTIONS[0].prompt)
      }
    })
  }
}

