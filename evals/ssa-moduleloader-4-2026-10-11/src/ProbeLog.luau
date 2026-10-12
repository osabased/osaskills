-- Each runtime gets its own copy of this table.
local ProbeLog = { events = {} }

function ProbeLog.record(name: string, detail: any?)
	table.insert(ProbeLog.events, { name = name, detail = detail })
end

function ProbeLog.count(name: string): number
	local n = 0
	for _, event in ProbeLog.events do
		if event.name == name then
			n += 1
		end
	end
	return n
end

function ProbeLog.details(name: string): { any }
	local found = {}
	for _, event in ProbeLog.events do
		if event.name == name then
			table.insert(found, event.detail)
		end
	end
	return found
end

return ProbeLog
