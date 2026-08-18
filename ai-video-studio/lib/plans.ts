export type PlanId = "starter" | "creator" | "enterprise";

export interface Plan {
  id: PlanId;
  badge?: string;
  name: string;          // zh-TW
  nameEn: string;        // EN sub-label
  price: number;         // NT$
  originalPrice?: number; // 劃線價（年繳優惠用）
  period: string;
  credits: number;
  creditLabel: string;
  validity: string;
  features: string[];
  highlight?: boolean;
  cta: string;
  requiresTaxId?: boolean;
}

export const PLANS: Plan[] = [
  {
    id: "starter",
    name: "新手體驗包",
    nameEn: "Starter Pack",
    price: 149,
    period: "一次性",
    credits: 500,
    creditLabel: "500 點",
    validity: "點數 30 天有效",
    features: [
      "500 生成點數",
      "點數 30 天內有效",
      "標準畫質輸出（1080p）",
      "基礎風格模型 3 款",
      "社群論壇支援",
    ],
    cta: "立即體驗",
  },
  {
    id: "creator",
    badge: "最受歡迎",
    name: "創作者月費",
    nameEn: "Creator Monthly",
    price: 890,
    originalPrice: 1200,
    period: "/ 月",
    credits: 3000,
    creditLabel: "3,000 點 / 月",
    validity: "點數每月自動更新",
    features: [
      "每月 3,000 生成點數",
      "點數月底自動更新",
      "4K 畫質輸出",
      "優先算圖佇列",
      "全部風格模型解鎖",
      "AI 音樂同步功能",
      "Email 技術支援",
    ],
    highlight: true,
    cta: "開始訂閱",
  },
  {
    id: "enterprise",
    name: "企業點數包",
    nameEn: "Enterprise Pack",
    price: 2990,
    period: "一次性",
    credits: 15000,
    creditLabel: "15,000 點",
    validity: "點數永久不過期",
    features: [
      "15,000 生成點數（永久有效）",
      "4K + 超解析輸出",
      "品牌模型微調（最多 3 組）",
      "專屬客服經理",
      "API 存取授權",
      "統一編號開立三聯式發票",
      "最多 5 組帳號共用",
    ],
    highlight: false,
    cta: "購買企業方案",
    requiresTaxId: true,
  },
];

export const CREDIT_COSTS = {
  "5s": 75,
  "10s": 140,
  "15s": 200,
} as const;
