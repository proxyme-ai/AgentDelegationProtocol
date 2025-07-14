interface BulkActionsBarProps {
  selectedCount: number;
  onAction: (action: string) => void;
  onClear: () => void;
}

export default function BulkActionsBar({ selectedCount, onAction, onClear }: BulkActionsBarProps) {
  return (
    <div className="alert alert-info mb-4">
      <div className="flex items-center justify-between w-full">
        <div className="flex items-center">
          <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-medium">
            {selectedCount} agent{selectedCount !== 1 ? 's' : ''} selected
          </span>
        </div>

        <div className="flex gap-2">
          {/* Status Actions */}
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-sm btn-success">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Activate
            </label>
            <ul tabIndex={0} className="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52">
              <li>
                <button onClick={() => onAction('activate')}>
                  ✅ Set to Active
                </button>
              </li>
              <li>
                <button onClick={() => onAction('deactivate')}>
                  ⏸️ Set to Inactive
                </button>
              </li>
              <li>
                <button onClick={() => onAction('suspend')}>
                  🚫 Suspend
                </button>
              </li>
            </ul>
          </div>

          {/* Delete Action */}
          <button
            className="btn btn-sm btn-error"
            onClick={() => onAction('delete')}
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>

          {/* Clear Selection */}
          <button
            className="btn btn-sm btn-ghost"
            onClick={onClear}
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}