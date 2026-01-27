// useReservationsStore.ts
import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { PERIOD_MODE, VIEW_MODE } from '@/common/constants/mode'
import { convertNullToUndefined } from '@/common/utils/convertNullToUndefined'
import type { UndefinedToNull } from '@/common/utils/convertUndefinedToNull'
import { getMockData } from '@/mocks/helpers'
import colWeeklyData from '@/mocks/reservations/colWeekly.json'
import staffDailyData from '@/mocks/reservations/staffDaily.json'
import unitDailyData from '@/mocks/reservations/unitDaily.json'
import weeklyData from '@/mocks/reservations/weekly.json'
import {
  toTimeGridColumnsFromDailyColumn,
  toTimeGridColumnsFromWeeklyColumn,
  toTimelineHeadersFromDailyColumn,
  toTimelineHeadersFromWeeklyColumn,
} from '@/models/reservations/utils'
import type { CommonResponse } from '@/types/common'
import type { ColWeekly, DailyReservations, WeeklyReservations } from '@/types/reservations'

export type ReservationsState = {
  // loading
  isDailyReservationsLoading: boolean
  isWeeklyReservationsLoading: boolean
  isWeeklyColumnReservationsLoading: boolean

  // 首次请求用
  needLoading: boolean

  // 列周
  weekViewColIds: Record<VIEW_MODE, string[]>

  // data
  dailyColumns: DailyReservations['columns']
  weeklyData: WeeklyReservations['dates']
  weeklyColumnData: Array<{ colId: string; dates: ColWeekly['dates'] }>

  // timeline
  timelineData: {
    displayColumnNum: number
    timeGridColumns: any[]
    headerColumns: any[]
  }

  // actions
  markQueryChanged: () => void

  fetchDailyReservations: (
    mode: VIEW_MODE,
    date: string,
    ids: string[],
    isSilent: boolean,
    cb?: () => void,
    failCb?: (e: any) => void,
  ) => Promise<void>

  fetchWeeklyReservations: (
    mode: VIEW_MODE,
    date: string,
    ids: string[],
    isSilent: boolean,
    cb?: () => void,
    failCb?: (e: any) => void,
  ) => Promise<void>

  fetchWeeklyColumnReservations: (
    colId: string,
    mode: VIEW_MODE,
    date: string,
    isSilent: boolean,
    cb?: () => void,
    failCb?: (e: any) => void,
  ) => Promise<void>

  toggleWeekViewColumn: (
    colId: string,
    viewMode: VIEW_MODE,
    date: string,
    cb?: () => void,
  ) => void

  setTimelineData: (
    date: string,
    viewMode: VIEW_MODE,
    periodMode: PERIOD_MODE,
    unitDisplayColumnNum: number,
    staffDisplayColumnNum: number,
  ) => void
}

export const useReservationsStore = create<ReservationsState>()(
  immer((set, get) => ({
    // =====================
    // initial state
    // =====================
    isDailyReservationsLoading: false,
    isWeeklyReservationsLoading: false,
    isWeeklyColumnReservationsLoading: false,

    needLoading: true,

    weekViewColIds: {
      [VIEW_MODE.UNIT]: [],
      [VIEW_MODE.STAFF]: [],
    },

    dailyColumns: [],
    weeklyData: [],
    weeklyColumnData: [],

    timelineData: {
      displayColumnNum: 1,
      timeGridColumns: [],
      headerColumns: [],
    },

    // =====================
    // helpers
    // =====================
    markQueryChanged: () => {
      set(state => {
        state.needLoading = true
      })
    },

    // =====================
    // fetch day
    // =====================
    fetchDailyReservations: async (mode, _date, _ids, isSilent, cb, failCb) => {
      set(state => {
        state.isDailyReservationsLoading = !isSilent && state.needLoading
      })

      try {
        const { weekViewColIds } = get()

        const [
          { data: { columns } },
          { data: { dates } },
        ] = await Promise.all([
          getMockData(
            mode === VIEW_MODE.STAFF ? staffDailyData : unitDailyData,
            10000,
          ) as Promise<CommonResponse<DailyReservations>>,

          weekViewColIds[mode].length > 0
            ? (getMockData(colWeeklyData, 500) as Promise<CommonResponse<ColWeekly>>)
            : Promise.resolve({ data: { dates: [] } }),
        ])

        const mockWeeklyColumnData = weekViewColIds[mode].map(colId => ({
          colId,
          dates,
        }))

        set(state => {
          state.dailyColumns = columns
          state.weeklyColumnData = mockWeeklyColumnData
          state.isDailyReservationsLoading = false
          state.needLoading = false
        })

        cb?.()
      } catch (e) {
        set(state => {
          state.isDailyReservationsLoading = false
          state.needLoading = false
        })
        failCb?.(e)
      }
    },

    // =====================
    // fetch week
    // =====================
    fetchWeeklyReservations: async (_mode, _date, _ids, isSilent, cb, failCb) => {
      set(state => {
        state.isWeeklyReservationsLoading = !isSilent && state.needLoading
      })

      try {
        const res = (await getMockData(weeklyData, 5000)) as unknown as UndefinedToNull<
          CommonResponse<WeeklyReservations>
        >
        const { data } = convertNullToUndefined(res)

        set(state => {
          state.weeklyData = data.dates
          state.isWeeklyReservationsLoading = false
          state.needLoading = false
        })

        cb?.()
      } catch (e) {
        set(state => {
          state.isWeeklyReservationsLoading = false
          state.needLoading = false
        })
        failCb?.(e)
      }
    },

    // =====================
    // fetch column week
    // =====================
    fetchWeeklyColumnReservations: async (colId, _mode, _date, isSilent, cb, failCb) => {
      set(state => {
        state.isWeeklyColumnReservationsLoading = !isSilent
      })

      try {
        const { data } = (await getMockData(colWeeklyData, 500)) as CommonResponse<ColWeekly>

        set(state => {
          state.weeklyColumnData = [...get().weeklyColumnData, { colId, dates: data.dates }]
          state.isWeeklyColumnReservationsLoading = false
        })

        cb?.()
      } catch (e) {
        set(state => {
          state.isWeeklyColumnReservationsLoading = false
        })
        failCb?.(e)
      }
    },

    // =====================
    // toggle column week
    // =====================
    toggleWeekViewColumn: (colId, viewMode, date, cb) => {
      const { weekViewColIds, weeklyColumnData, fetchWeeklyColumnReservations } = get()
      const prev = weekViewColIds[viewMode]
      const isWeekView = prev.includes(colId)

      if (isWeekView) {
        set(state => {
          state.weekViewColIds[viewMode] = prev.filter(id => id !== colId)
          state.weeklyColumnData = weeklyColumnData.filter(c => c.colId !== colId)
        })
        cb?.()
        return
      }

      set(state => {
        state.weekViewColIds[viewMode] = [...prev, colId]
      })

      fetchWeeklyColumnReservations(colId, viewMode, date, false, cb)
    },

    // =====================
    // build timeline
    // =====================
    setTimelineData: (date, viewMode, periodMode, unitDisplayColumnNum, staffDisplayColumnNum) => {
      const { dailyColumns, weeklyColumnData, weeklyData, weekViewColIds } = get()
      const weekCols = weekViewColIds[viewMode]

      if (periodMode === PERIOD_MODE.DAY) {
        const base =
          viewMode === VIEW_MODE.UNIT ? unitDisplayColumnNum : staffDisplayColumnNum
        const displayColumnNum =
          weekCols.length > 0 ? Math.min(dailyColumns.length, base) + 7 : base

        set(state => {
          state.timelineData.displayColumnNum = displayColumnNum
          state.timelineData.headerColumns = toTimelineHeadersFromDailyColumn(
            dailyColumns,
            weekCols,
            weeklyColumnData,
          )
          state.timelineData.timeGridColumns = toTimeGridColumnsFromDailyColumn(
            dailyColumns,
            date,
            weekCols,
            weeklyColumnData,
          )
        })
        return
      }

      const { columns, displayColumnNum } = toTimeGridColumnsFromWeeklyColumn(weeklyData)

      set(state => {
        state.timelineData.displayColumnNum = displayColumnNum
        state.timelineData.headerColumns = toTimelineHeadersFromWeeklyColumn(weeklyData)
        state.timelineData.timeGridColumns = columns
      })
    },
  })),
)



// useReservationsSWR.ts
import useSWR from 'swr'
import { useMemo } from 'react'
import { PERIOD_MODE, VIEW_MODE } from '@/common/constants/mode'
import { useReservationsStore } from './useReservationsStore'

type Params = {
  viewMode: VIEW_MODE
  periodMode: PERIOD_MODE
  date: string
  ids: string[]
  unitDisplayColumnNum: number
  staffDisplayColumnNum: number
}

export function useReservationsSWR(params: Params) {
  const store = useReservationsStore

  const key = useMemo(() => {
    return [
      'reservations',
      params.viewMode,
      params.periodMode,
      params.date,
      params.ids.join(','),
    ].join('|')
  }, [params.viewMode, params.periodMode, params.date, params.ids])

  useSWR(
    key,
    () => {
      const s = store.getState()

      const isSilent =
        s.isDailyReservationsLoading || s.isWeeklyReservationsLoading

      const onFetched = () => {
        s.setTimelineData(
          params.date,
          params.viewMode,
          params.periodMode,
          params.unitDisplayColumnNum,
          params.staffDisplayColumnNum,
        )
      }

      if (params.periodMode === PERIOD_MODE.WEEK) {
        s.fetchWeeklyReservations(
          params.viewMode,
          params.date,
          params.ids,
          isSilent,
          onFetched,
        )
      } else {
        s.fetchDailyReservations(
          params.viewMode,
          params.date,
          params.ids,
          isSilent,
          onFetched,
        )
      }
    },
    {
      refreshInterval: 40_000,
      revalidateOnFocus: false,
      keepPreviousData: true,
    },
  )
}







