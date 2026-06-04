import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

interface EfficiencyData {
  day: string
  autonomous: number
  manual: number
}

interface EfficiencyChartProps {
  data: EfficiencyData[]
  manualLabel?: string;
  autonomousLabel?: string;
}

export function EfficiencyChart({ data, manualLabel = "Manual", autonomousLabel = "Autonomous" }: EfficiencyChartProps) {
  return (
    <div className="h-[400px] w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <defs>
            <linearGradient id="colorAutonomous" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorManual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis 
            dataKey="day" 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `${value}`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
            itemStyle={{ color: '#f8fafc' }}
          />
          <Area
            type="monotone"
            dataKey="manual"
            name={manualLabel}
            stroke="#f59e0b"
            fillOpacity={1}
            fill="url(#colorManual)"
          />
          <Area
            type="monotone"
            dataKey="autonomous"
            name={autonomousLabel}
            stroke="#3b82f6"
            fillOpacity={1}
            fill="url(#colorAutonomous)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
