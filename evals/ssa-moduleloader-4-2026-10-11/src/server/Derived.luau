local Base = require(script.Parent.Base)

-- Defines no Init of its own; Base's Init should not run again with Derived as self.
return setmetatable({ Tag = "Derived" }, Base)
