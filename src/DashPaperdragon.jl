
module DashPaperdragon
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.92"

include("jl/dashpaperdragon.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "dash_paperdragon",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "dash_paperdragon.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_paperdragon.min.js.map",
    external_url = nothing,
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
