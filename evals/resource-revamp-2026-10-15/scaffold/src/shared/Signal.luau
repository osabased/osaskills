--!strict
export type Connection = { Disconnect: (self: Connection) -> () }
export type Signal<T...> = {
	Connect: (self: Signal<T...>, callback: (T...) -> ()) -> Connection,
	Fire: (self: Signal<T...>, T...) -> (),
	DisconnectAll: (self: Signal<T...>) -> (),
}

local Signal = {}

function Signal.new<T...>(): Signal<T...>
	local callbacks: { [(T...) -> ()]: true } = {}
	local signal = {}

	function signal:Connect(callback: (T...) -> ()): Connection
		callbacks[callback] = true
		local connection = {}
		function connection:Disconnect()
			callbacks[callback] = nil
		end
		return connection
	end

	function signal:Fire(...: T...)
		for callback in callbacks do
			task.spawn(callback, ...)
		end
	end

	function signal:DisconnectAll()
		table.clear(callbacks)
	end

	return signal :: any
end

return Signal
